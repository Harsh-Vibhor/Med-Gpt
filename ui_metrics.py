"""
Evaluation Metrics for Med-GPT UI
==================================
Reusable metric functions for computing answer quality scores.
"""

from sklearn.metrics.pairwise import cosine_similarity


def compute_answer_relevance(question, answer, embedding_model):
    """
    Compute relevance score between question and answer.

    Args:
        question: User question string
        answer: Generated answer string
        embedding_model: SentenceTransformer model

    Returns:
        float: Relevance score (0.0 to 1.0)
    """
    try:
        if not answer or len(answer.strip()) < 10:
            return 0.0

        question_emb = embedding_model.encode([question])[0]
        answer_emb = embedding_model.encode([answer])[0]

        similarity = cosine_similarity(
            question_emb.reshape(1, -1), answer_emb.reshape(1, -1)
        )[0][0]

        return float(similarity)
    except Exception as e:
        print(f"Error computing relevance: {e}")
        return 0.0


def compute_faithfulness(answer, retrieved_chunks, embedding_model):
    """
    Compute faithfulness score between answer and retrieved context.

    Args:
        answer: Generated answer string
        retrieved_chunks: List of retrieved chunk dictionaries
        embedding_model: SentenceTransformer model

    Returns:
        float: Faithfulness score (0.0 to 1.0)
    """
    try:
        if not answer or len(answer.strip()) < 10:
            return 0.0

        if not retrieved_chunks:
            return 0.0

        # Combine retrieved chunks into context
        context = " ".join([chunk["text"] for chunk in retrieved_chunks])

        if not context:
            return 0.0

        answer_emb = embedding_model.encode([answer])[0]
        context_emb = embedding_model.encode([context])[0]

        similarity = cosine_similarity(
            answer_emb.reshape(1, -1), context_emb.reshape(1, -1)
        )[0][0]

        return float(similarity)
    except Exception as e:
        print(f"Error computing faithfulness: {e}")
        return 0.0


def get_quality_badge(score):
    """
    Get quality badge emoji and text based on score.

    Args:
        score: Numeric score (0.0 to 1.0)

    Returns:
        tuple: (emoji, label, color)
    """
    if score >= 0.7:
        return "🟢", "High", "green"
    elif score >= 0.4:
        return "🟡", "Moderate", "orange"
    else:
        return "🔴", "Low", "red"


def compute_context_coverage(answer, retrieved_chunks, embedding_model, threshold=0.65):
    """
    Compute context coverage score - how many retrieved chunks are reflected in the answer.

    Args:
        answer: Generated answer string
        retrieved_chunks: List of retrieved chunk dictionaries
        embedding_model: SentenceTransformer model
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
        answer_emb = embedding_model.encode([answer])[0]

        # Count how many chunks are semantically reflected in the answer
        used_chunks = 0

        for chunk in retrieved_chunks:
            chunk_text = chunk.get("text", "")

            if not chunk_text:
                continue

            # Embed the chunk
            chunk_emb = embedding_model.encode([chunk_text])[0]

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


def get_coverage_badge(score):
    """
    Get coverage badge emoji and text based on coverage score.

    Args:
        score: Coverage score (0.0 to 1.0)

    Returns:
        tuple: (emoji, label, color)
    """
    if score >= 0.75:
        return "🟢", "High", "green"
    elif score >= 0.5:
        return "🟡", "Moderate", "orange"
    else:
        return "🔴", "Low", "red"
