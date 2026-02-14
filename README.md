# Med-GPT Project

## RAG Build Progress

- ✅ **Step 1: Document Ingestion** (PDF loading & text extraction) – Completed
- ✅ **Step 2: Text Chunking with Overlap** – Completed
- ✅ **Step 3: Embeddings Generation** (sentence-transformers) – Completed
- ✅ **Step 4: Vector Store Integration** (ChromaDB) – Completed
- ✅ **Step 5: LLM Answer Generation** (Ollama phi model) – Completed
- ✅ **Step 6: Streamlit UI** – Completed (Production-Ready with Chat-Style UX)

Complete RAG system with ultra-smooth, chat-style interface:
- **Chat-style UX** with user/assistant message bubbles (ChatGPT-like)
- **Keyboard submit** (Press Enter to submit queries)
- **Form-based submission** (eliminates UI flicker)
- **Session state management** (smooth, stable rendering)
- **Composite confidence scoring** with multiple interpretable parameters:
  - Retrieval confidence (similarity + consensus)
  - Coverage confidence (chunk count + context length)
  - Grounding confidence (answer quality checks)
  - Weighted average: 50% retrieval, 30% coverage, 20% grounding
- **Citation formatting** with document names and chunk numbers
- **Collapsible evidence viewer** (transparency without overwhelming)
- **Query suggestions** (contextual, based on indexed docs)
- **Medical disclaimer** footer
- Quality filtering (similarity >0.2, top-7 retrieval)

Run with: `streamlit run app.py`
