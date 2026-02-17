"""
Multi-Model Evaluation Pipeline for Med-GPT
============================================
Evaluates multiple Ollama models on medical RAG tasks with automatic metrics.

Usage:
    python evaluate_models.py

Output:
    - results/evaluation_results.csv
    - results/evaluation_results.json
    - results/model_statistics.csv
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import stats

# Import existing RAG pipeline
from ingest_documents import initialize_vector_store, enhanced_rag_query


# ===============================
# CONFIGURATION
# ===============================

MODELS = ["phi", "tinyllama", "gemma:2b"]

EVALUATION_QUESTIONS = [
    "What are the diagnostic criteria for severe malaria according to WHO?",
    "What is the recommended first-line treatment for uncomplicated malaria?",
    "What are the symptoms of severe malaria in children?",
    "How is malaria diagnosed in endemic areas?",
    "What are the prevention strategies for malaria recommended by WHO?",
    "What is the dosage of artemisinin-based combination therapy for adults?",
    "What are the complications of untreated severe malaria?",
    "When should parenteral artesunate be administered?",
    "What are the contraindications for antimalarial drugs?",
    "How should malaria in pregnancy be managed according to WHO guidelines?",
]

OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)


# ===============================
# EVALUATION METRICS
# ===============================


def compute_answer_relevance(question, answer, model):
    """
    Compute relevance score between question and answer.
    Uses cosine similarity of embeddings.
    """
    try:
        question_emb = model.encode([question])[0]
        answer_emb = model.encode([answer])[0]

        similarity = cosine_similarity(
            question_emb.reshape(1, -1), answer_emb.reshape(1, -1)
        )[0][0]

        return float(similarity)
    except Exception as e:
        print(f"Error computing relevance: {e}")
        return 0.0


def compute_faithfulness(answer, retrieved_chunks, model):
    """
    Compute faithfulness score between answer and retrieved context.
    Uses cosine similarity of embeddings.
    """
    try:
        if not retrieved_chunks:
            return 0.0

        # Combine retrieved chunks into context
        context = " ".join([chunk["text"] for chunk in retrieved_chunks])

        answer_emb = model.encode([answer])[0]
        context_emb = model.encode([context])[0]

        similarity = cosine_similarity(
            answer_emb.reshape(1, -1), context_emb.reshape(1, -1)
        )[0][0]

        return float(similarity)
    except Exception as e:
        print(f"Error computing faithfulness: {e}")
        return 0.0


def compute_context_coverage(answer, retrieved_chunks, model, threshold=0.65):
    """
    Compute context coverage score - how many retrieved chunks are reflected in the answer.

    Args:
        answer: Generated answer string
        retrieved_chunks: List of retrieved chunk dictionaries
        model: SentenceTransformer model
        threshold: Similarity threshold to consider a chunk as "used" (default: 0.65)

    Returns:
        float: Coverage score (0.0 to 1.0) - ratio of used chunks to total chunks
    """
    try:
        if not answer or len(answer.strip()) < 10:
            return 0.0

        if not retrieved_chunks:
            return 0.0

        # Embed the answer once
        answer_emb = model.encode([answer])[0]

        # Count how many chunks are semantically reflected in the answer
        used_chunks = 0

        for chunk in retrieved_chunks:
            chunk_text = chunk.get("text", "")

            if not chunk_text:
                continue

            # Embed the chunk
            chunk_emb = model.encode([chunk_text])[0]

            # Compute similarity
            similarity = cosine_similarity(
                answer_emb.reshape(1, -1), chunk_emb.reshape(1, -1)
            )[0][0]

            # Check if chunk is "used" (exceeds threshold)
            if similarity >= threshold:
                used_chunks += 1

        # Calculate coverage ratio
        coverage = used_chunks / len(retrieved_chunks)

        return float(coverage)

    except Exception as e:
        print(f"Error computing context coverage: {e}")
        return 0.0


# ===============================
# EVALUATION PIPELINE
# ===============================


def evaluate_single_model(model_name, questions, collection, embedding_model):
    """
    Evaluate a single Ollama model on all questions.
    Returns list of result dictionaries.
    """
    print(f"\n{'='*60}")
    print(f"Evaluating model: {model_name}")
    print(f"{'='*60}")

    results = []

    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}/{len(questions)}: {question[:60]}...")

        try:
            # Run RAG query with specific model
            rag_result = enhanced_rag_query(
                collection=collection,
                query=question,
                model=embedding_model,
                top_k=7,
                similarity_threshold=0.2,
            )

            answer = rag_result.get("answer", "")
            retrieved_chunks = rag_result.get("retrieved_chunks", [])
            confidence = rag_result.get("confidence", 0)

            # Compute automatic metrics
            relevance_score = compute_answer_relevance(
                question, answer, embedding_model
            )

            faithfulness_score = compute_faithfulness(
                answer, retrieved_chunks, embedding_model
            )

            coverage_score = compute_context_coverage(
                answer, retrieved_chunks, embedding_model
            )

            # Store result
            result = {
                "question": question,
                "model": model_name,
                "answer": answer,
                "num_retrieved_chunks": len(retrieved_chunks),
                "retrieved_chunks": json.dumps(
                    [
                        {
                            "document": chunk["document_name"],
                            "chunk_index": chunk["chunk_index"],
                            "similarity": chunk["similarity"],
                            "text_preview": chunk["text"][:200],
                        }
                        for chunk in retrieved_chunks
                    ]
                ),
                "confidence": confidence,
                "relevance_score": relevance_score,
                "faithfulness_score": faithfulness_score,
                "coverage_score": coverage_score,
                "human_score": None,  # To be filled manually
                "timestamp": datetime.now().isoformat(),
            }

            results.append(result)

            print(f"  ✓ Answer generated ({len(answer)} chars)")
            print(f"  ✓ Relevance: {relevance_score:.3f}")
            print(f"  ✓ Faithfulness: {faithfulness_score:.3f}")
            print(f"  ✓ Coverage: {coverage_score:.3f}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append(
                {
                    "question": question,
                    "model": model_name,
                    "answer": f"ERROR: {str(e)}",
                    "num_retrieved_chunks": 0,
                    "retrieved_chunks": "[]",
                    "confidence": 0,
                    "relevance_score": 0.0,
                    "faithfulness_score": 0.0,
                    "coverage_score": 0.0,
                    "human_score": None,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    return results


def compute_model_statistics(df):
    """
    Compute aggregated statistics per model.
    """
    stats_list = []

    for model in df["model"].unique():
        model_df = df[df["model"] == model]

        stats_dict = {
            "model": model,
            "num_questions": len(model_df),
            "mean_relevance": model_df["relevance_score"].mean(),
            "std_relevance": model_df["relevance_score"].std(),
            "mean_faithfulness": model_df["faithfulness_score"].mean(),
            "std_faithfulness": model_df["faithfulness_score"].std(),
            "mean_coverage": model_df["coverage_score"].mean(),
            "std_coverage": model_df["coverage_score"].std(),
            "mean_confidence": model_df["confidence"].mean(),
            "std_confidence": model_df["confidence"].std(),
            "combined_score": (
                model_df["relevance_score"].mean() * 0.33
                + model_df["faithfulness_score"].mean() * 0.33
                + model_df["coverage_score"].mean() * 0.34
            ),
        }

        stats_list.append(stats_dict)

    return pd.DataFrame(stats_list)


def compute_statistical_significance(df):
    """
    Compute paired t-test between models for relevance and faithfulness.
    """
    print("\n" + "=" * 60)
    print("STATISTICAL SIGNIFICANCE TESTS (Paired t-test)")
    print("=" * 60)

    models = df["model"].unique()

    if len(models) < 2:
        print("Need at least 2 models for comparison.")
        return

    # Compare each pair of models
    for i, model1 in enumerate(models):
        for model2 in models[i + 1 :]:
            print(f"\n{model1} vs {model2}:")

            # Get scores for both models
            m1_df = df[df["model"] == model1].sort_values("question")
            m2_df = df[df["model"] == model2].sort_values("question")

            # Relevance comparison
            t_stat_rel, p_val_rel = stats.ttest_rel(
                m1_df["relevance_score"], m2_df["relevance_score"]
            )

            # Faithfulness comparison
            t_stat_faith, p_val_faith = stats.ttest_rel(
                m1_df["faithfulness_score"], m2_df["faithfulness_score"]
            )

            print(
                f"  Relevance: t={t_stat_rel:.3f}, p={p_val_rel:.4f} {'*' if p_val_rel < 0.05 else ''}"
            )
            print(
                f"  Faithfulness: t={t_stat_faith:.3f}, p={p_val_faith:.4f} {'*' if p_val_faith < 0.05 else ''}"
            )


# ===============================
# MAIN EVALUATION
# ===============================


def run_evaluation():
    """
    Main evaluation pipeline.
    """
    print("=" * 60)
    print("Med-GPT Multi-Model Evaluation Pipeline")
    print("=" * 60)
    print(f"Models: {', '.join(MODELS)}")
    print(f"Questions: {len(EVALUATION_QUESTIONS)}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Initialize RAG system
    print("\nInitializing RAG system...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    _, collection = initialize_vector_store()
    print("✓ RAG system ready")

    # Evaluate all models
    all_results = []

    for model_name in MODELS:
        model_results = evaluate_single_model(
            model_name=model_name,
            questions=EVALUATION_QUESTIONS,
            collection=collection,
            embedding_model=embedding_model,
        )
        all_results.extend(model_results)

    # Create DataFrame
    df = pd.DataFrame(all_results)

    # Compute statistics
    stats_df = compute_model_statistics(df)

    # Save results
    csv_path = OUTPUT_DIR / "evaluation_results.csv"
    json_path = OUTPUT_DIR / "evaluation_results.json"
    stats_path = OUTPUT_DIR / "model_statistics.csv"

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)
    stats_df.to_csv(stats_path, index=False)

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"\n✓ Results saved to: {csv_path}")
    print(f"✓ JSON saved to: {json_path}")
    print(f"✓ Statistics saved to: {stats_path}")

    # Display statistics
    print("\n" + "=" * 60)
    print("MODEL STATISTICS")
    print("=" * 60)
    print(stats_df.to_string(index=False))

    # Statistical significance
    compute_statistical_significance(df)

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Review results in: results/evaluation_results.csv")
    print("2. Add human scores (1-5) to the 'human_score' column")
    print("3. Use results for research paper tables and analysis")
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation()
