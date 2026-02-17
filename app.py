"""
Med-GPT Professional Medical AI Platform
=========================================
Production-ready medical decision support interface
"""

import streamlit as st
from sentence_transformers import SentenceTransformer
from ingest_documents import initialize_vector_store, enhanced_rag_query
from ui_metrics import (
    compute_answer_relevance,
    compute_faithfulness,
    compute_context_coverage,
    get_quality_badge,
    get_coverage_badge,
)

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Med-GPT | Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# PROFESSIONAL MEDICAL THEME STYLING
# ==============================================================================
st.markdown(
    """
<style>
    /* ========== GLOBAL THEME ========== */
    :root {
        --primary-bg: #0a1929;
        --secondary-bg: #132f4c;
        --card-bg: #1a2332;
        --accent-teal: #00bfa5;
        --accent-blue: #2196f3;
        --text-primary: #e3f2fd;
        --text-secondary: #90caf9;
        --border-color: #263238;
        --success: #00e676;
        --warning: #ffd54f;
        --error: #ff5252;
    }
    
    /* ========== MAIN CONTAINER ========== */
    .main {
        background: linear-gradient(135deg, #0a1929 0%, #132f4c 100%);
        padding: 0;
    }
    
    /* ========== HEADER BAR ========== */
    .header-container {
        background: linear-gradient(90deg, #1a2332 0%, #263238 100%);
        border-bottom: 2px solid var(--accent-teal);
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin: 0.25rem 0 0 0;
        font-weight: 400;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    
    .status-online {
        background: rgba(0, 230, 118, 0.15);
        color: var(--success);
        border: 1px solid var(--success);
    }
    
    .model-badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(33, 150, 243, 0.15);
        color: var(--accent-blue);
        border: 1px solid var(--accent-blue);
        margin-left: 0.5rem;
    }
    
    /* ========== ANSWER CARD ========== */
    .answer-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        border: 1px solid var(--border-color);
    }
    
    .question-header {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }
    
    .answer-text {
        font-size: 1.15rem;
        line-height: 1.8;
        color: var(--text-primary);
        margin: 1rem 0 1.5rem 0;
    }
    
    /* ========== METRICS STRIP ========== */
    .metric-card {
        background: linear-gradient(135deg, #1a2332 0%, #263238 100%);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        border: 1px solid var(--border-color);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 191, 165, 0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-teal);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .metric-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .badge-high {
        background: rgba(0, 230, 118, 0.2);
        color: var(--success);
    }
    
    .badge-moderate {
        background: rgba(255, 213, 79, 0.2);
        color: var(--warning);
    }
    
    .badge-low {
        background: rgba(255, 82, 82, 0.2);
        color: var(--error);
    }
    
    /* ========== EVIDENCE PANEL ========== */
    .evidence-panel {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid var(--accent-teal);
        border: 1px solid var(--border-color);
    }
    
    .evidence-header {
        font-size: 1rem;
        color: var(--accent-teal);
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .evidence-chunk {
        background: rgba(0, 191, 165, 0.05);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        border-left: 3px solid var(--accent-teal);
    }
    
    /* ========== COMPARISON PANEL ========== */
    .comparison-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
    }
    
    .model-result-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .best-model-glow {
        box-shadow: 0 0 20px rgba(0, 230, 118, 0.3);
        border: 2px solid var(--success);
    }
    
    /* ========== INPUT BAR ========== */
    .stChatInput {
        border-radius: 24px !important;
        border: 2px solid var(--border-color) !important;
        background: var(--card-bg) !important;
    }
    
    .stChatInput:focus-within {
        border-color: var(--accent-teal) !important;
        box-shadow: 0 0 0 3px rgba(0, 191, 165, 0.1) !important;
    }
    
    /* ========== BUTTONS ========== */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-blue) 100%);
        color: white;
        border: none;
        border-radius: 24px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 191, 165, 0.4);
    }
    
    /* ========== SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a2332 0%, #0a1929 100%);
        border-right: 1px solid var(--border-color);
    }
    
    /* ========== PROGRESS BAR ========== */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent-teal) 0%, var(--accent-blue) 100%);
        border-radius: 10px;
    }
    
    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {
        background: var(--card-bg);
        border-radius: 8px;
        color: var(--text-primary);
        font-weight: 600;
    }
    
    /* ========== SPACING ========== */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.model = None
    st.session_state.collection = None
    st.session_state.messages = []
    st.session_state.processing = False
    st.session_state.selected_model = "phi"
    st.session_state.compare_mode = False


# ==============================================================================
# BACKEND FUNCTIONS (UNCHANGED)
# ==============================================================================
@st.cache_resource
def load_rag():
    """Load RAG system components."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    _, collection = initialize_vector_store()
    return model, collection


def get_indexed_documents(collection):
    """Get list of unique indexed documents."""
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


# ==============================================================================
# INITIALIZE SYSTEM
# ==============================================================================
if not st.session_state.initialized:
    with st.spinner("🔄 Initializing Med-GPT system..."):
        model, collection = load_rag()
        st.session_state.model = model
        st.session_state.collection = collection
        st.session_state.initialized = True

# ==============================================================================
# PROFESSIONAL HEADER BAR
# ==============================================================================
st.markdown(
    f"""
<div class="header-container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="header-title">🏥 Med-GPT</h1>
            <p class="header-subtitle">Evidence-grounded medical assistant powered by WHO guidelines</p>
        </div>
        <div>
            <span class="status-badge status-online">● ONLINE</span>
            <span class="model-badge">🧠 {st.session_state.selected_model.upper()}</span>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# SIDEBAR - MODEL SELECTION & CONTROLS
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # Model selector
    available_models = ["phi", "tinyllama", "gemma:2b"]
    st.session_state.selected_model = st.selectbox(
        "🧠 Select Model",
        available_models,
        index=available_models.index(st.session_state.selected_model),
        help="Choose the Ollama model for answer generation",
    )

    st.markdown("---")

    # System info
    st.markdown("### 📊 System Information")
    st.info(f"**Embedding Model:** all-MiniLM-L6-v2")
    st.info(f"**Knowledge Base:** WHO Medical Guidelines")
    st.info(f"**Retrieval:** Top-7 semantic chunks")

    st.markdown("---")

    # Session controls
    st.markdown("### 🗂️ Session")
    message_count = len(st.session_state.messages)
    st.caption(f"**Messages:** {message_count}")

    if st.button("🧹 Clear Conversation", use_container_width=True):
        if "confirm_clear" not in st.session_state:
            st.session_state.confirm_clear = False
        st.session_state.confirm_clear = True

    if st.session_state.get("confirm_clear", False):
        st.warning("⚠️ Clear all messages?")
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
    st.caption(
        "⚠️ **Disclaimer:** For educational use only. Not a substitute for professional medical advice."
    )

# ==============================================================================
# MAIN CONTENT AREA - CONVERSATION DISPLAY
# ==============================================================================

# Display conversation history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # User message
        st.markdown(
            f"""
        <div style="text-align: right; margin: 1rem 0;">
            <div style="display: inline-block; background: rgba(33, 150, 243, 0.15); 
                        border-radius: 16px; padding: 0.75rem 1.25rem; max-width: 70%;
                        border: 1px solid rgba(33, 150, 243, 0.3);">
                <p style="margin: 0; color: #e3f2fd; font-size: 1rem;">{msg["content"]}</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    elif msg["role"] == "assistant":
        # Assistant message with professional card layout
        meta = msg.get("meta", {})

        # Main answer card
        st.markdown(
            f"""
        <div class="answer-card">
            <div class="question-header">📋 Medical Response</div>
            <div class="answer-text">{msg["content"]}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Confidence bar
        if meta.get("confidence") is not None:
            confidence = meta["confidence"]
            st.progress(confidence / 100, text=f"Confidence: {confidence}%")
            st.caption(
                "_Confidence based on semantic similarity with retrieved guidelines_"
            )

        # Metrics strip (horizontal cards)
        if meta.get("sources") and meta.get("user_query"):
            st.markdown("<br>", unsafe_allow_html=True)

            # Compute metrics
            relevance = compute_answer_relevance(
                meta.get("user_query", ""), msg["content"], st.session_state.model
            )

            faithfulness = compute_faithfulness(
                msg["content"], meta["sources"], st.session_state.model
            )

            coverage = compute_context_coverage(
                msg["content"], meta["sources"], st.session_state.model
            )

            # Display metrics in horizontal cards
            col1, col2, col3 = st.columns(3)

            with col1:
                rel_emoji, rel_label, _ = get_quality_badge(relevance)
                st.markdown(
                    f"""
                <div class="metric-card">
                    <div class="metric-label">🎯 Relevance</div>
                    <div class="metric-value">{relevance:.2f}</div>
                    <div class="metric-badge badge-{rel_label.lower()}">{rel_emoji} {rel_label}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col2:
                faith_emoji, faith_label, _ = get_quality_badge(faithfulness)
                st.markdown(
                    f"""
                <div class="metric-card">
                    <div class="metric-label">✓ Faithfulness</div>
                    <div class="metric-value">{faithfulness:.2f}</div>
                    <div class="metric-badge badge-{faith_label.lower()}">{faith_emoji} {faith_label}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            with col3:
                cov_emoji, cov_label, _ = get_coverage_badge(coverage)
                st.markdown(
                    f"""
                <div class="metric-card">
                    <div class="metric-label">📊 Coverage</div>
                    <div class="metric-value">{coverage:.2f}</div>
                    <div class="metric-badge badge-{cov_label.lower()}">{cov_emoji} {cov_label}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        # Evidence panel (collapsible)
        if meta.get("sources"):
            num_sources = len(meta["sources"])

            with st.expander(
                f"🔬 Research Evidence ({num_sources} guideline sections)",
                expanded=False,
            ):
                st.markdown(
                    f"""
                <div class="evidence-header">
                    💡 Why this answer? Based on {num_sources} WHO guideline section{'s' if num_sources != 1 else ''}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                for idx, chunk in enumerate(meta["sources"][:5], 1):
                    similarity_pct = chunk["similarity"] * 100
                    doc_name = chunk.get("document_name", "Unknown")
                    chunk_text = chunk["text"][:300]

                    st.markdown(
                        f"""
                    <div class="evidence-chunk">
                        <strong>[{idx}] {doc_name}</strong> 
                        <span style="color: var(--accent-teal); font-size: 0.85rem;">
                            (Similarity: {similarity_pct:.1f}%)
                        </span>
                        <p style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                            {chunk_text}...
                        </p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# MODEL COMPARISON FEATURE
# ==============================================================================
if len(st.session_state.messages) > 0:
    # Get last user question
    last_user_msg = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break

    if last_user_msg and not st.session_state.compare_mode:
        if st.button("🔄 Compare All Models", use_container_width=True):
            st.session_state.compare_mode = True
            st.rerun()

# Show comparison results
if st.session_state.compare_mode and len(st.session_state.messages) > 0:
    # Get last user question
    last_user_msg = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break

    if last_user_msg:
        st.markdown("---")
        st.markdown("### 🔄 Multi-Model Comparison")
        st.caption(f"**Question:** {last_user_msg}")

        available_models = ["phi", "tinyllama", "gemma:2b"]
        comparison_results = []

        # Run all models sequentially
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, model_name in enumerate(available_models):
            status_text.text(f"⚙️ Running {model_name}...")

            try:
                result = enhanced_rag_query(
                    st.session_state.collection,
                    last_user_msg,
                    st.session_state.model,
                    top_k=7,
                    similarity_threshold=0.2,
                    ollama_model=model_name,
                )

                answer = result.get("answer", "")
                sources = result.get("retrieved_chunks", [])
                confidence = result.get("confidence", 0)

                # Compute metrics
                relevance = compute_answer_relevance(
                    last_user_msg, answer, st.session_state.model
                )
                faithfulness = compute_faithfulness(
                    answer, sources, st.session_state.model
                )
                coverage = compute_context_coverage(
                    answer, sources, st.session_state.model
                )
                combined_score = (relevance + faithfulness + coverage) / 3

                comparison_results.append(
                    {
                        "model": model_name,
                        "answer": answer,
                        "confidence": confidence,
                        "relevance": relevance,
                        "faithfulness": faithfulness,
                        "coverage": coverage,
                        "combined_score": combined_score,
                        "sources": sources,
                    }
                )

            except Exception as e:
                comparison_results.append(
                    {
                        "model": model_name,
                        "answer": f"Error: {str(e)}",
                        "confidence": 0,
                        "relevance": 0,
                        "faithfulness": 0,
                        "coverage": 0,
                        "combined_score": 0,
                        "sources": [],
                    }
                )

            progress_bar.progress((i + 1) / len(available_models))

        status_text.empty()
        progress_bar.empty()

        # Find best model
        best_model = max(comparison_results, key=lambda x: x["combined_score"])

        # Display results
        for result in comparison_results:
            is_best = result["model"] == best_model["model"]

            with st.expander(
                f"{'🏆 ' if is_best else ''}**{result['model'].upper()}** - Combined Score: {result['combined_score']:.2f}",
                expanded=is_best,
            ):
                # Answer
                st.markdown(
                    f"""
                <div class="{'comparison-card best-model-glow' if is_best else 'comparison-card'}">
                    <div class="answer-text">{result['answer']}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Metrics in 4 columns
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    rel_emoji, rel_label, _ = get_quality_badge(result["relevance"])
                    st.metric(
                        "Relevance",
                        f"{result['relevance']:.2f}",
                        f"{rel_emoji} {rel_label}",
                    )

                with col2:
                    faith_emoji, faith_label, _ = get_quality_badge(
                        result["faithfulness"]
                    )
                    st.metric(
                        "Faithfulness",
                        f"{result['faithfulness']:.2f}",
                        f"{faith_emoji} {faith_label}",
                    )

                with col3:
                    cov_emoji, cov_label, _ = get_coverage_badge(result["coverage"])
                    st.metric(
                        "Coverage",
                        f"{result['coverage']:.2f}",
                        f"{cov_emoji} {cov_label}",
                    )

                with col4:
                    st.metric("Confidence", f"{result['confidence']}%")

                st.caption(f"📚 Retrieved {len(result['sources'])} chunks")

        # Close button
        if st.button("✖ Close Comparison", use_container_width=True):
            st.session_state.compare_mode = False
            st.rerun()

# ==============================================================================
# CHAT INPUT (FIXED BOTTOM)
# ==============================================================================
query = st.chat_input(
    "Ask a medical question (e.g., How is severe malaria treated according to WHO?)"
)

if query and not st.session_state.processing:
    st.session_state.processing = True

    # Store user message
    st.session_state.messages.append({"role": "user", "content": query})

    # Generate answer
    with st.spinner("🔄 Generating evidence-based answer..."):
        try:
            result = enhanced_rag_query(
                st.session_state.collection,
                query,
                st.session_state.model,
                top_k=7,
                similarity_threshold=0.2,
                ollama_model=st.session_state.selected_model,
            )

            answer = result.get("answer", "")

            # Check if answer is valid
            is_empty = not answer or answer.strip() == ""
            is_timeout = "took too long to respond" in answer.lower()
            is_error = "error" in answer.lower() and len(answer) < 100

            if is_empty or is_timeout or is_error:
                # Failed answer
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "⚠️ Unable to generate a complete answer. Please try rephrasing your question or check if the Ollama service is running.",
                        "meta": {
                            "confidence": None,
                            "sources": [],
                            "user_query": query,
                        },
                    }
                )
            else:
                # Valid answer
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "meta": {
                            "confidence": result.get("confidence", 0),
                            "sources": result.get("retrieved_chunks", []),
                            "user_query": query,
                        },
                    }
                )

            # Limit conversation memory
            if len(st.session_state.messages) > 6:
                st.session_state.messages = st.session_state.messages[-6:]

        except Exception as e:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"⚠️ Error generating answer: {str(e)}",
                    "meta": {},
                }
            )

            if len(st.session_state.messages) > 6:
                st.session_state.messages = st.session_state.messages[-6:]

    st.session_state.processing = False
    st.rerun()
