# Step 5: Ollama LLM Integration for Answer Generation

## Purpose

Completing the RAG pipeline with a local LLM enables:
- **Answer Generation**: Convert retrieved context into natural language answers
- **Privacy**: All processing happens locally, no cloud APIs
- **Cost-Effective**: No API fees or usage limits
- **Customization**: Full control over model selection and prompting

## What Was Added

This step integrates Ollama local LLM for answer generation:

1. **`call_ollama()` function**: Makes HTTP requests to local Ollama API
2. **`rag_query()` function**: Complete RAG workflow:
   - Retrieves top-k relevant chunks from ChromaDB
   - Builds context-aware prompt with truncation
   - Generates answer using Ollama phi model
   - Displays retrieved chunks and generated answer
3. **Context truncation**: Limits context to 1500 characters to avoid long prompts

## Ollama Configuration

**API Endpoint**: `http://localhost:11434/api/generate`  
**Model**: `phi` (lightweight, fast, suitable for medical Q&A)  
**Context Limit**: 1500 characters (prevents token overflow)

### Prerequisites

1. Install Ollama: [https://ollama.ai](https://ollama.ai)
2. Pull phi model: `ollama pull phi`
3. Start Ollama server: `ollama serve`

## RAG Workflow

### Step-by-Step Process

```
1. User Query → Encode to embedding
2. ChromaDB Search → Retrieve top 3 similar chunks
3. Build Context → Concatenate chunk texts (truncate if needed)
4. Build Prompt → System instruction + Context + Question
5. Call Ollama → Generate answer using phi model
6. Display Results → Show chunks + answer
```

### Prompt Template

```
You are a helpful medical assistant. Answer the question based ONLY on the provided context. If the answer cannot be found in the context, say "I don't have enough information to answer that question."

Context:
{retrieved_chunks}

Question: {user_query}

Answer:
```

This enforces **context-only answering** to prevent hallucinations.

## Sample Queries

The pipeline automatically runs three test queries:
1. "What is diabetes?"
2. "What are the symptoms of diabetes?"
3. "How is diabetes treated?"

### Output Format

For each query:
- **Retrieved Chunks**: Document name, chunk index, similarity score
- **Generated Answer**: Natural language response from Ollama

## Technical Details

### API Call

```python
payload = {
    "model": "phi",
    "prompt": prompt,
    "stream": False
}
response = requests.post("http://localhost:11434/api/generate", json=payload)
```

### Error Handling

- Connection errors → Displays helpful message to start Ollama
- API errors → Returns error description
- Missing model → User prompted to pull phi model

### Context Truncation

```python
if len(full_context) > max_context_length:
    full_context = full_context[:max_context_length] + "..."
```

Prevents token overflow while preserving most relevant information.

## What Is NOT Included Yet

This implementation completes the core RAG pipeline. The following are **not yet implemented**:

- ❌ **User Interface**: No Streamlit/web UI (as per requirements)
- ❌ **Interactive Mode**: No continuous query loop
- ❌ **Advanced Features**: No re-ranking, query expansion, or hybrid search
- ❌ **Production Features**: No logging, monitoring, or deployment config

## Next Steps

The RAG system is now complete and ready for:
1. Streamlit UI for user-friendly interaction
2. Query history and session management
3. Advanced retrieval techniques
4. Production deployment

## Performance Notes

**phi Model**:
- Lightweight (~2.7GB)
- Fast inference on consumer hardware
- Good for medical Q&A tasks
- Runs entirely locally

**Alternative Models**:
- `llama2` - More capable, larger
- `mistral` - Better reasoning
- `medllama2` - Medical-specific (if available)
