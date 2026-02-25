import sys
from pathlib import Path

# Ensure project root is importable when Streamlit runs this script directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import streamlit as st
from app.graph.graph import build_graph
from app.graph.state import GraphState

graph = build_graph()


def _state_get(state_obj, key, default=None):
    if isinstance(state_obj, dict):
        return state_obj.get(key, default)
    return getattr(state_obj, key, default)

st.title("Enterprise AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you?"}
    ]
if "awaiting_upload" not in st.session_state:
    st.session_state.awaiting_upload = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:

    st.session_state.messages.append(
        {"role":"user","content":user_input}
    )
    st.chat_message("user").write(user_input)

    assistant_box = st.chat_message("assistant")
    with assistant_box:
        with st.spinner("Thinking..."):
            state = GraphState(
                user_input=user_input,
                uploaded_file=st.session_state.uploaded_file
            )

            result = graph.invoke(state)

    st.session_state.awaiting_upload = _state_get(result, "needs_upload", False)
    assistant_response = _state_get(result, "response", "No response generated.")
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
