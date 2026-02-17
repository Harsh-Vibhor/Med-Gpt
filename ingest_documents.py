"""
Document Ingestion Script for RAG System
=========================================
This script loads PDF files from a local folder, extracts text content,
splits it into chunks, generates embeddings, stores them in ChromaDB,
and exposes RAG query utilities for Streamlit.
"""

import os
from pathlib import Path
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import requests


# ===============================
# PDF INGESTION PIPELINE
# ===============================


def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {str(e)}")
        return ""


def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start += chunk_size - overlap

        if end >= len(words):
            break

    return chunks


def generate_embeddings(chunks, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    texts = [c["chunk_text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    for i, chunk in enumerate(chunks):
        chunk["embedding_vector"] = embeddings[i]

    return chunks, model


def initialize_vector_store(
    collection_name="medical_docs", persist_directory="data/chroma_db"
):
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection(name=collection_name)
    return client, collection


def store_embeddings(collection, chunks):
    ids, embeddings, documents, metadatas = [], [], [], []

    for chunk in chunks:
        ids.append(f"{chunk['document_name']}_chunk_{chunk['chunk_index']}")
        embeddings.append(
            chunk["embedding_vector"].tolist()
            if hasattr(chunk["embedding_vector"], "tolist")
            else chunk["embedding_vector"]
        )
        documents.append(chunk["chunk_text"])
        metadatas.append(
            {
                "document_name": chunk["document_name"],
                "chunk_index": chunk["chunk_index"],
            }
        )

    collection.add(
        ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
    )


def ingest_documents(docs_folder="data/docs"):
    docs_path = Path(docs_folder)
    if not docs_path.exists():
        print(f"Folder not found: {docs_folder}")
        return []

    pdf_files = list(docs_path.glob("*.pdf"))
    if not pdf_files:
        print("No PDFs found.")
        return []

    all_chunks = []

    for pdf in pdf_files:
        text = extract_text_from_pdf(pdf)
        chunks = chunk_text(text)

        for idx, chunk in enumerate(chunks):
            all_chunks.append(
                {"document_name": pdf.name, "chunk_index": idx, "chunk_text": chunk}
            )

    return all_chunks


# ===============================
# OLLAMA CALL
# ===============================


def call_ollama(
    prompt, model="tinyllama", ollama_url="http://localhost:11434/api/generate"
):
    """
    Call Ollama API with timeout protection and hard generation limits.
    Returns graceful error message if timeout occurs.
    """
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 384, "temperature": 0.2, "top_p": 0.9},
        }

        response = requests.post(ollama_url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "")

    except requests.exceptions.Timeout:
        return "The model took too long to respond."

    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {str(e)}"

    except Exception as e:
        return f"Error calling Ollama: {str(e)}"


# ===============================
# ENHANCED RAG QUERY
# ===============================


def enhanced_rag_query(
    collection, query, model, top_k=7, similarity_threshold=0.05, ollama_model="phi"
):
    """
    Streamlit-safe RAG query with similarity filtering,
    deterministic context construction, and confidence scoring.

    Args:
        collection: ChromaDB collection
        query: User question
        model: SentenceTransformer model for embeddings
        top_k: Number of chunks to retrieve
        similarity_threshold: Minimum similarity threshold
        ollama_model: Ollama model name (phi, tinyllama, gemma:2b, etc.)
    """

    # 1. Encode query
    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    retrieved_chunks = []

    for i in range(len(results["documents"][0])):
        similarity = 1 - results["distances"][0][i]

        if similarity >= similarity_threshold:
            retrieved_chunks.append(
                {
                    "document_name": results["metadatas"][0][i]["document_name"],
                    "chunk_index": results["metadatas"][0][i]["chunk_index"],
                    "text": results["documents"][0][i],
                    "similarity": similarity,
                }
            )

    # ------------------------------------------------------------------
    # 2️⃣ NO CONTEXT → GENERAL MEDICAL FALLBACK
    # ------------------------------------------------------------------
    if not retrieved_chunks:
        prompt = f"""
You are a medical assistant.

Give a GENERAL medical explanation.
This answer is NOT based on WHO or retrieved guidelines.

Question:
{query}

Answer briefly (3-5 lines):
"""
        answer = call_ollama(prompt, model=ollama_model)

        return {
            "answer": answer.strip(),
            "confidence": 10,
            "retrieved_chunks": [],
            "insufficient_context": True,
        }

    # ------------------------------------------------------------------
    # 3️⃣ BUILD CONTEXT (TOP 1–2 CHUNKS ONLY)
    # ------------------------------------------------------------------
    context_parts = [chunk["text"][:500] for chunk in retrieved_chunks[:2]]
    context = "\n\n".join(context_parts)

    # ------------------------------------------------------------------
    # 4️⃣ GUIDELINE-GROUNDED PROMPT
    # ------------------------------------------------------------------
    prompt = f"""
You are a medical assistant answering strictly from WHO guideline excerpts.

Context:
{context}

Question:
{query}

Instructions:
- Use ONLY the context
- Be concise (3-5 lines)
- If partially unclear, answer what is known

Answer:
"""
    answer = call_ollama(prompt, model=ollama_model).strip()

    # ------------------------------------------------------------------
    # 5️⃣ CONFIDENCE + SAFETY LOGIC
    # ------------------------------------------------------------------
    avg_similarity = sum(c["similarity"] for c in retrieved_chunks) / len(
        retrieved_chunks
    )

    if answer:
        confidence = min(100, int(avg_similarity * 100))
        insufficient = avg_similarity < 0.25
    else:
        answer = (
            "Relevant WHO guideline sections were retrieved, "
            "but the local model could not generate a reliable answer."
        )
        confidence = min(40, int(avg_similarity * 60))
        insufficient = True

    return {
        "answer": answer,
        "confidence": confidence,
        "retrieved_chunks": retrieved_chunks,
        "insufficient_context": insufficient,
    }


# ===============================
# INGESTION ENTRY POINT
# ===============================

if __name__ == "__main__":
    chunks = ingest_documents("data/docs")

    if chunks:
        chunks, model = generate_embeddings(chunks)
        _, collection = initialize_vector_store()
        store_embeddings(collection, chunks)
        print("✅ Ingestion complete.")
    else:
        print("❌ No documents ingested.")
