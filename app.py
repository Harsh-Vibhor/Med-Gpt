"""
Med-GPT RAG System — ChatGPT-Style UI (STABLE)
=============================================
✔ Single input (st.chat_input)
✔ Conversation history
✔ No duplicate rendering
✔ Immediate answer display
✔ RAG + confidence + sources
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
from ingest_documents import initialize_vector_store, enhanced_rag_query

# ------------------------------------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Med-GPT RAG System", page_icon="🏥", layout="wide")

# ------------------------------------------------------------------------------
# CUSTOM CSS FOR TEXT SELECTION
# ------------------------------------------------------------------------------
st.markdown(
    """
<style>
    /* Custom text selection styling for evidence blocks */
    .evidence-text::selection {
        background-color: rgba(200, 200, 200, 0.3);  /* Subtle gray */
        color: inherit;  /* Keep original text color */
    }
    
    .evidence-text::-moz-selection {
        background-color: rgba(200, 200, 200, 0.3);  /* Firefox support */
        color: inherit;
    }
    
    /* Override Streamlit's default mark tag styling in evidence containers */
    .evidence-container mark,
    .evidence-text mark {
        background-color: transparent;
        color: inherit;
        padding: 0;
    }
    
    /* Style for the evidence container */
    .evidence-container {
        padding: 8px;
        margin: 6px 0;
        border-left: 3px solid #555;
        background-color: transparent;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------------------
# SESSION STATE (SINGLE SOURCE OF TRUTH)
# ------------------------------------------------------------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.model = None
    st.session_state.collection = None
    st.session_state.messages = []
    st.session_state.processing = False  # 🔥 prevents double execution


# ------------------------------------------------------------------------------
# LOAD RAG SYSTEM (CACHED)
# ------------------------------------------------------------------------------
@st.cache_resource
def load_rag():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    _, collection = initialize_vector_store()
    return model, collection


def get_indexed_documents(collection):
    """Get list of unique indexed documents from ChromaDB."""
    try:
        results = collection.get()
        if results and results["metadatas"]:
            doc_names = set()
            for metadata in results["metadatas"]:
                if "document_name" in metadata:
                    doc_names.add(metadata["document_name"])
            return sorted(list(doc_names))
        return []
    except Exception:
        return []


def generate_refinement_suggestions(collection, user_query=""):
    """Generate 2-3 query refinement suggestions based on user query keywords."""

    # Detect topic keywords from query
    query_lower = user_query.lower()

    # Medical topic keywords
    topics = {
        "malaria": ["malaria", "plasmodium", "antimalarial"],
        "diabetes": ["diabetes", "glucose", "insulin", "glycemic"],
        "hypertension": ["hypertension", "blood pressure", "bp"],
        "tuberculosis": ["tuberculosis", "tb", "mycobacterium"],
        "hiv": ["hiv", "aids", "antiretroviral"],
    }

    # Detect query intent
    intent_keywords = {
        "treatment": ["treat", "therapy", "medication", "drug", "management"],
        "diagnosis": ["diagnose", "diagnostic", "test", "criteria", "screening"],
        "symptoms": ["symptom", "sign", "presentation", "manifestation"],
        "prevention": ["prevent", "prophylaxis", "vaccination", "immunization"],
        "complications": ["complication", "adverse", "side effect", "risk"],
    }

    # Identify topic
    detected_topic = None
    for topic, keywords in topics.items():
        if any(kw in query_lower for kw in keywords):
            detected_topic = topic
            break

    # Identify intent
    detected_intent = None
    for intent, keywords in intent_keywords.items():
        if any(kw in query_lower for kw in keywords):
            detected_intent = intent
            break

    # Generate contextual suggestions
    suggestions = []

    if detected_topic:
        # Topic-specific suggestions
        if detected_topic == "malaria":
            suggestions = [
                "What are the diagnostic criteria for severe malaria?",
                "What is the recommended treatment for uncomplicated malaria?",
                "What are the prevention strategies for malaria?",
            ]
        elif detected_topic == "diabetes":
            suggestions = [
                "What are the diagnostic criteria for type 2 diabetes?",
                "What are the recommended blood glucose targets?",
                "What are the complications of uncontrolled diabetes?",
            ]
        elif detected_topic == "hypertension":
            suggestions = [
                "What are the blood pressure targets for hypertension?",
                "What is the first-line treatment for hypertension?",
                "What are the complications of untreated hypertension?",
            ]
        elif detected_topic == "tuberculosis":
            suggestions = [
                "What is the standard treatment regimen for TB?",
                "What are the diagnostic tests for tuberculosis?",
                "What is the duration of TB treatment?",
            ]
        elif detected_topic == "hiv":
            suggestions = [
                "What is the recommended antiretroviral therapy for HIV?",
                "What are the WHO criteria for starting ART?",
                "What are the opportunistic infections in HIV?",
            ]
    else:
        # Generic guideline-focused suggestions
        suggestions = [
            "What are the WHO treatment guidelines for this condition?",
            "What are the diagnostic criteria according to WHO?",
            "What are the recommended prevention strategies?",
        ]

    return suggestions[:3]


# ------------------------------------------------------------------------------
# INITIALIZE SYSTEM ONCE
# ------------------------------------------------------------------------------
if not st.session_state.initialized:
    with st.spinner("Loading Med-GPT RAG System..."):
        model, collection = load_rag()
        st.session_state.model = model
        st.session_state.collection = collection
        st.session_state.initialized = True


# ------------------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------------------
st.title("🏥 Med-GPT RAG System")
st.caption("Ask questions about medical documents and get AI-powered answers.")
st.markdown("---")

# ------------------------------------------------------------------------------
# CONVERSATION DISPLAY
# ------------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and "meta" in msg:
            meta = msg["meta"]

            # Confidence visualization (only if confidence is available)
            if meta.get("confidence") is not None:
                # Answer Quality Badge (above confidence bar)
                if meta["confidence"] >= 70:
                    st.markdown("**Answer Quality:** 🟢 High confidence")
                elif meta["confidence"] >= 40:
                    st.markdown("**Answer Quality:** 🟡 Moderate confidence")
                else:
                    st.markdown("**Answer Quality:** 🔴 Low confidence")

                st.markdown(f"**Confidence:** {meta['confidence']}% ℹ️")
                st.caption(
                    "_Confidence is based on semantic similarity between the question and retrieved guideline sections. It does not measure clinical certainty._"
                )

                # Progress bar
                st.progress(meta["confidence"] / 100)

                # Show query refinement suggestions for low confidence
                if meta["confidence"] < 40:
                    st.markdown("---")
                    st.markdown("💡 **Try asking a more specific question:**")

                    # Pass user query for keyword-based suggestions
                    user_query = meta.get("user_query", "")
                    suggestions = generate_refinement_suggestions(
                        st.session_state.collection, user_query
                    )
                    for suggestion in suggestions:
                        st.markdown(f"• _{suggestion}_")
            else:
                # Failed answer generation - show subtle warning
                st.warning(
                    "⚠️ Unable to generate a complete answer. Try asking a more specific question."
                )

            # Sources (always show if available)
            if meta.get("sources"):
                # Show count of retrieved sections
                num_sources = len(meta["sources"])

                # "Why this answer?" explanation
                st.markdown("")  # Spacing
                st.info(
                    f"💡 **Why this answer?** This answer is based on {num_sources} WHO guideline section{'s' if num_sources != 1 else ''} retrieved from the knowledge base."
                )

                st.caption(
                    f"_Retrieved {num_sources} guideline section{'s' if num_sources != 1 else ''}_"
                )

                with st.expander("📚 View sources and evidence", expanded=False):
                    st.markdown("**Sources:**")
                    for src in meta["sources"]:
                        st.markdown(
                            f"- {src['document_name']} — chunk {src['chunk_index']}"
                        )

                    st.markdown("---")
                    st.markdown("**Retrieved Evidence:**")
                    for i, src in enumerate(meta["sources"], 1):
                        st.markdown(f"**Chunk {i}**")

                        # Highlight first 1-2 sentences
                        chunk_text = src["text"][:300]
                        try:
                            # Simple sentence detection (split on . ! ?)
                            sentences = []
                            current = ""
                            for char in chunk_text:
                                current += char
                                if char in ".!?" and len(current.strip()) > 10:
                                    sentences.append(current.strip())
                                    current = ""
                                    if len(sentences) >= 2:
                                        break

                            if sentences:
                                # Highlight first 1-2 sentences
                                highlighted = " ".join(sentences)
                                remaining = chunk_text[len(highlighted) :].strip()

                                # Use HTML with custom classes for selection styling
                                st.markdown(
                                    f'<div class="evidence-container"><div class="evidence-text">'
                                    f'<span class="evidence-highlight">{highlighted}</span>'
                                    f"{remaining}…"
                                    f"</div></div>",
                                    unsafe_allow_html=True,
                                )
                            else:
                                # Fallback: no highlighting
                                st.markdown(
                                    f'<div class="evidence-container"><div class="evidence-text">{chunk_text}…</div></div>',
                                    unsafe_allow_html=True,
                                )
                        except:
                            # Fallback: display normal text
                            st.markdown(
                                f'<div class="evidence-container"><div class="evidence-text">{chunk_text}…</div></div>',
                                unsafe_allow_html=True,
                            )

                        st.markdown("---")


# ------------------------------------------------------------------------------
# CHAT INPUT (BOTTOM — SINGLE INPUT)
# ------------------------------------------------------------------------------
query = st.chat_input(
    "Ask a medical question (e.g. How is severe malaria treated according to WHO?)"
)

if query and not st.session_state.processing:
    st.session_state.processing = True  # 🔒 lock

    # 1️⃣ Store user message
    st.session_state.messages.append({"role": "user", "content": query})

    # 2️⃣ Generate answer
    with st.spinner("Generating answer..."):
        try:
            result = enhanced_rag_query(
                st.session_state.collection,
                query,
                st.session_state.model,
                top_k=7,
                similarity_threshold=0.2,
            )

            # Check if answer is valid (not empty, None, or timeout message)
            answer = result.get("answer", "")

            # Detect empty or timeout responses
            is_empty = not answer or answer.strip() == ""
            is_timeout = "took too long to respond" in answer.lower()

            if is_empty or is_timeout:
                # Store error message WITHOUT confidence/sources
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "⚠️ The model could not generate an answer within the time limit.",
                    }
                )
            else:
                # Valid answer - store with metadata
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "meta": {
                            "confidence": result.get("confidence", 0),
                            "sources": result.get("retrieved_chunks", []),
                            "user_query": query,  # Store user query for context-aware suggestions
                        },
                    }
                )

            # Limit conversation memory to last 6 messages
            if len(st.session_state.messages) > 6:
                st.session_state.messages = st.session_state.messages[-6:]

        except Exception as e:
            st.session_state.messages.append(
                {"role": "assistant", "content": f"⚠️ Error generating answer: {str(e)}"}
            )

            # Limit conversation memory to last 6 messages
            if len(st.session_state.messages) > 6:
                st.session_state.messages = st.session_state.messages[-6:]

    st.session_state.processing = False

    # 🔥 THIS IS THE KEY FIX
    st.rerun()


# ------------------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------------------
with st.sidebar:
    # App Identity
    st.title("🏥 Med-GPT")
    st.markdown("**Medical RAG Assistant**")
    st.caption("WHO guideline-based inference")

    st.markdown("---")

    # System Status
    st.caption("SYSTEM STATUS")
    st.success("✓ System Online")

    # Model & Inference
    st.caption("MODEL & INFERENCE")
    st.info("🧠 Phi (Local)")
    st.caption("Embeddings: all-MiniLM-L6-v2 • Offline mode")

    # Knowledge Base
    st.caption("KNOWLEDGE BASE")
    st.info("📚 WHO Medical Guidelines")
    st.caption("Semantic search • 7 chunks retrieved")

    st.markdown("---")

    # Session Controls
    st.caption("SESSION")
    message_count = len(st.session_state.messages)
    st.caption(f"Messages: **{message_count}** • Local inference")

    if st.button("🧹 Clear Chat", use_container_width=True):
        if "confirm_clear" not in st.session_state:
            st.session_state.confirm_clear = False
        st.session_state.confirm_clear = True

    if st.session_state.get("confirm_clear", False):
        st.warning("Clear conversation?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Yes", use_container_width=True):
                st.session_state.messages = []
                st.session_state.confirm_clear = False
                st.rerun()
        with col2:
            if st.button("✗ No", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()

    st.markdown("---")

    # Footer
    st.caption("⚠️ Educational use only")
    st.caption("Not a substitute for professional medical advice")
