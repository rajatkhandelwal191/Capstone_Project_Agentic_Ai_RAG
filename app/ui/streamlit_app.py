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

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask something...")

if user_input:

    st.session_state.messages.append(
        {"role":"user","content":user_input}
    )

    state = GraphState(user_input=user_input)

    result = graph.invoke(state)

    if _state_get(result, "needs_upload", False):

        uploaded = st.file_uploader(
            "Upload RFP PDF",
            type=["pdf"]
        )

        if uploaded:

            upload_dir = PROJECT_ROOT / "temp_uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            path = upload_dir / uploaded.name

            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())

            st.success("File uploaded successfully.")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": _state_get(result, "response", "No response generated."),
        }
    )

    st.rerun()
