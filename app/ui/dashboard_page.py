from pathlib import Path

import streamlit as st

from app.core.config import Settings


def _read_text(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8")


def _render_overview():
    st.markdown(
        """
<div class="hero-card">
  <h3>Implementation Dashboard</h3>
  <p>
    This project is a production-style agentic assistant built on LangGraph. It routes each user request
    into one of four paths (RAG, Tool, RFP, Upload), supports cloud and local runtime modes, and lets you
    switch chat providers with environment variables (`ollama`, `gemini`, `groq`) without code changes.
  </p>
  <div class="chip-wrap">
    <span class="chip">LangGraph Supervisor Routing</span>
    <span class="chip">Qdrant + FAISS Retrieval</span>
    <span class="chip">Groq / Gemini / Ollama Switching</span>
    <span class="chip chip-warn">Secrets + Config Driven</span>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("APP_ENV", Settings.APP_ENV)
    m2.metric("LLM Provider", Settings.resolved_llm_provider())
    m3.metric("Vector Backend", "Qdrant" if Settings.USE_CLOUD else "FAISS")
    m4.metric("Graph Nodes", "5")
    m5.metric("RAG Top-K", str(Settings.RAG_TOP_K))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
<div class="detail-card">
  <h4>What You Built</h4>
  <p>A multi-agent enterprise assistant with deterministic intent routing, retrieval-augmented generation, database tooling, and upload-aware proposal generation.</p>
</div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
<div class="detail-card">
  <h4>Why It Matters</h4>
  <p>The architecture cleanly separates orchestration, retrieval, model provider selection, and data ingestion. This makes cloud deployment and provider failover practical.</p>
</div>
            """,
            unsafe_allow_html=True,
        )


def _render_system_flow_tab(project_root: Path):
    st.subheader("1) End-to-End System Flow")
    st.graphviz_chart(
        """
digraph G {
  rankdir=LR;
  node [shape=box style="rounded,filled" fillcolor="#1f2937" color="#64748b" fontcolor="#e5e7eb" fontname="Helvetica"];
  start [label="User Message"];
  state [label="GraphState(user_input, request_id, uploaded_file)"];
  supervisor [label="supervisor_node / router.classify_intent"];
  rag [label="rag_node -> run_rag_flow"];
  tool [label="tool_node -> run_tool_flow"];
  rfp [label="rfp_node -> run_rfp_flow"];
  upload [label="upload_node (needs_upload=True)"];
  ui [label="Streamlit UI renders response"];

  start -> state -> supervisor;
  supervisor -> rag [label="RAG_FLOW"];
  supervisor -> tool [label="TOOL_FLOW"];
  supervisor -> rfp [label="RFP_FLOW"];
  supervisor -> upload [label="UPLOAD_FLOW"];
  rag -> ui;
  tool -> ui;
  rfp -> ui;
  upload -> ui;
}
        """
    )

    st.markdown(
        """
**Routing strategy**
- Deterministic keyword hints first (fast and reliable).
- LLM fallback classification only for ambiguous prompts.
- Intent values map directly to graph edges in `app/graph/graph.py`.

**Graph state fields**
- `user_input`, `request_id`, `intent`, `response`, `uploaded_file`, `needs_upload`.
        """
    )

    st.subheader("2) Mermaid Flow (Source of Truth)")
    mermaid = _read_text(project_root / "docs" / "graph_flow.mmd", "docs/graph_flow.mmd not found.")
    st.code(mermaid, language="mermaid")


def _render_models_tab():
    st.subheader("LLM + Embeddings Architecture")
    st.markdown(
        """
| Layer | Local Mode | Cloud Mode |
|---|---|---|
| Chat model | `ChatOllama` | `ChatGoogleGenerativeAI` or `ChatGroq` |
| Embeddings | `OllamaEmbeddings` | `GoogleGenerativeAIEmbeddings` |
| Vector store | FAISS | Qdrant |
| Switching key | `APP_ENV`, `LLM_PROVIDER` | `APP_ENV`, `LLM_PROVIDER` |
        """
    )

    st.markdown(
        """
**Provider switch logic (`app/core/llm.py`)**
1. Resolve provider from `LLM_PROVIDER` (`auto`, `gemini`, `groq`, `ollama`).
2. Build provider client with corresponding API key/model env variables.
3. Return the correct LangChain chat model instance.

**Current cloud pattern**
- Chat: Groq (`llama-3.1-8b-instant`) for fast responses and no Gemini generation quota block.
- Retrieval embeddings: Gemini embedding model for Qdrant vector search.
        """
    )

    st.info(
        "Important: In cloud mode, even if chat uses Groq, RAG retrieval still needs Gemini embedding credentials."
    )


def _render_data_tab():
    st.subheader("Qdrant Ingestion & Retrieval Design")
    st.graphviz_chart(
        """
digraph G {
  rankdir=LR;
  node [shape=box style="rounded,filled" fillcolor="#1f2937" color="#64748b" fontcolor="#e5e7eb" fontname="Helvetica"];
  pdf [label="PDFs (kb_pdfs/)"];
  sqlite [label="SQLite tables\\nincidents + service_requests"];
  synthetic [label="Synthetic dataset\\nJSONL/JSON/CSV/TXT"];
  split [label="RecursiveCharacterTextSplitter\\nchunk=1000 overlap=200"];
  embed [label="Embeddings"];
  qdrant [label="Qdrant collection"];
  search [label="similarity_search(k=RAG_TOP_K)"];
  ctx [label="Context assembled\\nfor RAG prompt"];

  pdf -> split;
  sqlite -> split;
  synthetic -> split;
  split -> embed -> qdrant -> search -> ctx;
}
        """
    )

    st.markdown(
        """
**Ingestion command**
```powershell
poetry run python -m app.rag.ingest_qdrant
```

**What ingestion script does**
1. Loads PDFs.
2. Loads synthetic records.
3. Reads SQLite rows and converts each row to document text.
4. Chunks all documents.
5. Creates Qdrant collection if needed.
6. Upserts with deterministic point IDs (UUIDv5).

**Deterministic upsert**
- Point ID = UUIDv5(`upsert_key + chunk_index`).
- Re-runs update existing points instead of creating duplicates.

**Payload compatibility**
- Stores both `text` and `page_content` in payload.
- Retrieval uses `QDRANT_CONTENT_PAYLOAD_KEY` (default: `text`) to avoid empty context.
        """
    )

    st.subheader("SQLite Sources")
    st.markdown(
        """
- `incidents(id, title, severity, team, status, created_at)`
- `service_requests(id, department, request_type, status, created_at)`

Tool flow reads from repository layer, filters non-closed rows, and formats chat output.
        """
    )


def _render_config_tab():
    st.subheader("Config File Strategy (`app/core/config.py`)")
    st.markdown(
        """
The config layer resolves values in this order:
1. OS environment variables (`os.getenv`)
2. Streamlit secrets (`st.secrets`)
3. code defaults

This is why the same code works locally and in Streamlit Cloud.
        """
    )

    st.subheader("Local `.env` Example")
    st.code(
        """
APP_ENV=local
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:latest
EMBED_MODEL=nomic-embed-text
LOCAL_FAISS_PATH=app/rag/faiss_index
TEMPERATURE=0.2
RAG_TOP_K=4
        """.strip(),
        language="env",
    )

    st.subheader("Cloud Secrets Example (Groq chat + Qdrant + Gemini embeddings)")
    st.code(
        """
APP_ENV="cloud"
LLM_PROVIDER="groq"
TEMPERATURE="0.2"
RAG_TOP_K="4"

GROQ_API_KEY="YOUR_GROQ_KEY"
GROQ_MODEL="llama-3.1-8b-instant"

GOOGLE_API_KEY="YOUR_GEMINI_KEY"
GEMINI_EMBED_MODEL="gemini-embedding-001"

QDRANT_URL="https://<cluster>.cloud.qdrant.io"
QDRANT_API_KEY="YOUR_QDRANT_KEY"
QDRANT_COLLECTION="capstone_kb"
QDRANT_CONTENT_PAYLOAD_KEY="text"
        """.strip(),
        language="toml",
    )

    st.subheader("Resolved Runtime Snapshot")
    st.json(
        {
            "APP_ENV": Settings.APP_ENV,
            "USE_CLOUD": Settings.USE_CLOUD,
            "LLM_PROVIDER_RESOLVED": Settings.resolved_llm_provider(),
            "GEMINI_CHAT_MODEL": Settings.GEMINI_CHAT_MODEL,
            "GEMINI_EMBED_MODEL": Settings.GEMINI_EMBED_MODEL,
            "GROQ_MODEL": Settings.GROQ_MODEL,
            "QDRANT_COLLECTION": Settings.QDRANT_COLLECTION,
            "QDRANT_CONTENT_PAYLOAD_KEY": Settings.QDRANT_CONTENT_PAYLOAD_KEY,
            "RAG_TOP_K": Settings.RAG_TOP_K,
        }
    )


def _render_langgraph_tab():
    st.subheader("LangGraph Implementation Notes")
    st.markdown(
        """
**Files**
- `app/graph/graph.py`: node registration + conditional edges.
- `app/graph/nodes.py`: node handlers (`supervisor`, `rag`, `tool`, `rfp`, `upload`).
- `app/graph/router.py`: intent classification.
- `app/graph/state.py`: shared state contract.

**Node responsibilities**
- `supervisor`: classify and set `state.intent`.
- `rag`: query vector store and generate grounded response.
- `tool`: call SQLite-backed tools and return structured data.
- `rfp`: generate proposal text with optional uploaded PDF context.
- `upload`: set `needs_upload=True`.

**Design choices**
- Deterministic routing avoids expensive model calls for common intents.
- LLM fallback classification only when hints conflict or are ambiguous.
- Each flow is independently testable and observable via logs.
        """
    )

    st.subheader("Flow Trigger Cheat Sheet")
    st.markdown(
        """
| User Intent Example | Route |
|---|---|
| `show open incidents` | `TOOL_FLOW` |
| `draft proposal for cloud migration` | `RFP_FLOW` |
| `I want to upload an RFP` | `UPLOAD_FLOW` |
| `what is our sla policy` | `RAG_FLOW` |
        """
    )


def _render_deploy_tab():
    st.subheader("Streamlit Cloud Deployment")
    st.markdown(
        """
1. Push repo to GitHub.
2. Create Streamlit app with entrypoint `app/ui/streamlit_app.py`.
3. Add cloud secrets.
4. Ensure Qdrant data is already ingested.
5. Redeploy and verify startup logs.
        """
    )

    st.code(
        """
poetry run python -m app.db.init_db
poetry run python -m app.db.seed_db
poetry run python -m app.rag.ingest_qdrant
poetry run streamlit run app/ui/streamlit_app.py
        """.strip(),
        language="powershell",
    )

    st.subheader("Observability & Troubleshooting")
    st.markdown(
        """
- `backend=FAISS` in cloud: secrets/env not loaded, or `APP_ENV` not cloud.
- `context_chars` unexpectedly tiny: payload key mismatch; verify `QDRANT_CONTENT_PAYLOAD_KEY`.
- 429 quota errors: switch `LLM_PROVIDER` to `groq` or update Gemini billing/quota.
- If upload flow doesn't appear: verify routing trigger terms include upload/document intent.
- Rotate keys immediately if they were ever posted publicly.
        """
    )


def render_implementation_dashboard(project_root: Path):
    st.title("Implementation Dashboard")
    _render_overview()
    tab_flow, tab_langgraph, tab_models, tab_data, tab_config, tab_deploy = st.tabs(
        [
            "System Flow",
            "LangGraph",
            "Models & Embeddings",
            "Qdrant & Data",
            "Config & Env",
            "Deployment & Ops",
        ]
    )

    with tab_flow:
        _render_system_flow_tab(project_root)
    with tab_langgraph:
        _render_langgraph_tab()
    with tab_models:
        _render_models_tab()
    with tab_data:
        _render_data_tab()
    with tab_config:
        _render_config_tab()
    with tab_deploy:
        _render_deploy_tab()
