import sys
import time
from uuid import uuid4
from pathlib import Path

# Ensure project root is importable when Streamlit runs this script directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import streamlit as st
from app.graph.graph import build_graph
from app.graph.state import GraphState
from app.core.config import Settings
from app.core.logger import logger

graph = build_graph()
logger.info(
    "UI startup config | app_env=%s | use_cloud=%s | llm_provider=%s | qdrant_url_set=%s",
    Settings.APP_ENV,
    Settings.USE_CLOUD,
    Settings.resolved_llm_provider(),
    bool(Settings.QDRANT_URL),
)


def _state_get(state_obj, key, default=None):
    if isinstance(state_obj, dict):
        return state_obj.get(key, default)
    return getattr(state_obj, key, default)


def _log_preview(text: str, max_chars: int = 280) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= max_chars:
        return clean
    return clean[:max_chars] + "..."


st.title("Enterprise AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you?"}
    ]
if "awaiting_upload" not in st.session_state:
    st.session_state.awaiting_upload = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "show_faq" not in st.session_state:
    st.session_state.show_faq = False
if "show_question_guide" not in st.session_state:
    st.session_state.show_question_guide = False
if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None

top_col_left, top_col_faq, top_col_questions = st.columns([6, 1, 2])
with top_col_faq:
    if st.button("FAQ"):
        st.session_state.show_faq = not st.session_state.show_faq
with top_col_questions:
    if st.button("What To Ask"):
        st.session_state.show_question_guide = not st.session_state.show_question_guide

if st.session_state.show_faq:
    st.info(
        """
**How to use this chatbot**
- Ask normal questions to get knowledge-base answers and guidance.
- Ask incident/request-style questions (for example: open incidents or service request status) to trigger tool-based responses.
- Ask RFP/proposal questions directly, or upload an RFP PDF when prompted and then ask follow-up questions about that document.

**What this chatbot does**
- Routes your message to the right flow: RAG knowledge answers, operational tool lookups, or RFP response support.
- Accepts PDF uploads for document-driven proposal and analysis tasks.

**How it responds**
- Provides direct, context-aware text answers in the chat.
- If your request needs a file first, it asks for upload and continues once the PDF is provided.
"""
    )

if st.session_state.show_question_guide:
    st.markdown("### RAG FLOW (Knowledge Base)")
    st.caption("Click any question to send it.")
    rag_questions = [
        "What is our SLA policy?",
        "What uptime do we guarantee?",
        "Explain cloud architecture capabilities.",
        "What is our incident escalation process?",
        "How do we handle high severity incidents?",
        "What deployment strategy do we use?",
    ]
    for idx, question in enumerate(rag_questions):
        if st.button(question, key=f"rag_sample_q_{idx}", use_container_width=True):
            st.session_state.pending_user_input = question

    st.markdown("### TOOL FLOW (Database)")
    tool_questions = [
        "Show open incidents",
        "List P1 incidents",
        "Any network team incidents?",
        "Show all service requests",
        "Show pending requests",
    ]
    for idx, question in enumerate(tool_questions):
        if st.button(question, key=f"tool_sample_q_{idx}", use_container_width=True):
            st.session_state.pending_user_input = question
    st.caption("Expected: structured data output with IDs like INCxxxx / RITMxxxx")

    st.markdown("### RFP FLOW")
    rfp_questions = [
        "Draft proposal for cloud migration",
        "Create bid response for high availability system",
        "Write RFP response for scalable architecture",
        "Summarize this client requirement and propose solution",
    ]
    for idx, question in enumerate(rfp_questions):
        if st.button(question, key=f"rfp_sample_q_{idx}", use_container_width=True):
            st.session_state.pending_user_input = question
    st.caption("Expected: enterprise-style proposal text")

    st.markdown("### UPLOAD FLOW")
    upload_questions = [
        "I want to upload an RFP",
        "Summarize my uploaded document",
        "Analyze this client proposal",
    ]
    for idx, question in enumerate(upload_questions):
        if st.button(question, key=f"upload_sample_q_{idx}", use_container_width=True):
            st.session_state.pending_user_input = question

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

typed_input = st.chat_input("Ask something...")
if typed_input:
    user_input = typed_input
elif st.session_state.pending_user_input:
    user_input = st.session_state.pending_user_input
    st.session_state.pending_user_input = None
else:
    user_input = None

if user_input:
    request_id = str(uuid4())[:8]
    logger.info(
        "request_id=%s | Incoming user message | text=%s | has_uploaded_file=%s",
        request_id,
        user_input,
        bool(st.session_state.uploaded_file),
    )

    st.session_state.messages.append(
        {"role":"user","content":user_input}
    )
    st.chat_message("user").write(user_input)

    assistant_box = st.chat_message("assistant")
    with assistant_box:
        with st.spinner("Thinking..."):
            start = time.perf_counter()
            state = GraphState(
                user_input=user_input,
                request_id=request_id,
                uploaded_file=st.session_state.uploaded_file
            )

            try:
                result = graph.invoke(state)
            except Exception as exc:
                logger.exception("request_id=%s | Graph invocation failed | error=%s", request_id, exc)
                error_text = str(exc)
                if "ResourceExhausted" in error_text or "429" in error_text or "quota" in error_text.lower():
                    result = GraphState(
                        response=(
                            "Gemini quota exceeded (429). Please retry later, add billing/quota, "
                            "or set APP_ENV=local to use Ollama."
                        ),
                        needs_upload=False,
                    )
                else:
                    result = GraphState(
                        response="The request failed due to a runtime error. Check logs and retry.",
                        needs_upload=False,
                    )
            elapsed_ms = (time.perf_counter() - start) * 1000.0

    logger.info(
        "request_id=%s | Graph completed | intent=%s | needs_upload=%s | response_chars=%s | elapsed_ms=%.2f",
        request_id,
        _state_get(result, "intent", None),
        _state_get(result, "needs_upload", False),
        len(_state_get(result, "response", "") or ""),
        elapsed_ms,
    )
    st.session_state.awaiting_upload = _state_get(result, "needs_upload", False)
    assistant_response = _state_get(result, "response", "No response generated.")
    logger.info(
        "request_id=%s | Assistant response preview=%s",
        request_id,
        _log_preview(assistant_response),
    )
    assistant_box.write(assistant_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_response,
        }
    )

if st.session_state.awaiting_upload:
    uploaded = st.file_uploader(
        "Upload RFP PDF",
        type=["pdf"],
        key="rfp_pdf_uploader"
    )

    if uploaded:
        logger.info(
            "Received uploaded PDF | file_name=%s | size_bytes=%s",
            uploaded.name,
            uploaded.size,
        )
        upload_dir = PROJECT_ROOT / "temp_uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        path = upload_dir / uploaded.name

        with open(path, "wb") as f:
            f.write(uploaded.getbuffer())

        st.session_state.uploaded_file = str(path)
        st.session_state.awaiting_upload = False
        st.session_state.pop("rfp_pdf_uploader", None)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"Uploaded `{uploaded.name}` successfully. Ask your RFP question now."
            }
        )
        st.rerun()
