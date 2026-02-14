# Step 2: Text Chunking

## Purpose

In RAG (Retrieval-Augmented Generation) systems, chunking is essential because:
- **LLM Context Limits**: Language models have token limits; entire documents cannot fit in context
- **Semantic Granularity**: Smaller chunks improve retrieval precision by matching specific relevant passages
- **Efficient Retrieval**: Chunked text enables vector similarity search at a granular level
- **Better Context**: Overlapping chunks ensure important information isn't lost at chunk boundaries

## What Was Added

This step extends the document ingestion pipeline with text chunking capabilities:

1. **`chunk_text()` function**: Splits extracted text into overlapping chunks
2. **Chunk metadata storage**: Each chunk is stored with:
   - `document_name`: Source PDF filename
   - `chunk_index`: Position in the document
   - `chunk_text`: The actual text content
3. **Enhanced output**: Displays chunk statistics and previews

## Chunking Parameters

- **Chunk Size**: ~500 words per chunk
- **Overlap**: ~100 words between consecutive chunks
- **Rationale**: 
  - 500 words provides sufficient context for semantic understanding
  - 100-word overlap prevents information loss at boundaries

## Algorithm Overview

```
1. Split document text into individual words
2. Create chunks:
   - Take 500 words starting from current position
   - Join words into a text chunk
   - Move forward by 400 words (500 - 100 overlap)
3. Repeat until all text is processed
4. Store each chunk with metadata
```

**Example**:
- Chunk 0: words 0-499
- Chunk 1: words 400-899 (100-word overlap with Chunk 0)
- Chunk 2: words 800-1299 (100-word overlap with Chunk 1)

## What Is NOT Included Yet

This implementation focuses solely on text chunking. The following components are **not yet implemented**:

- ❌ **Embeddings**: No vector representations of chunks
- ❌ **Vector Database**: No storage system for embeddings (e.g., FAISS, Pinecone, ChromaDB)
- ❌ **LLM Integration**: No language model for generation
- ❌ **Retrieval Logic**: No similarity search or query processing

## Next Steps

The chunked text is now ready for:
1. Embedding generation (converting chunks to vectors)
2. Vector database storage
3. Retrieval and generation pipeline
