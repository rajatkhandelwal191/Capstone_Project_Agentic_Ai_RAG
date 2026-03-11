import sys
from pathlib import Path

import streamlit as st

# Ensure project root is importable when Streamlit runs this script directly.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import Settings
from app.core.logger import logger
from app.graph.graph import build_graph
from app.ui.chat_page import render_chat_page
from app.ui.dashboard_page import render_implementation_dashboard
from app.ui.styles import apply_global_styles

st.set_page_config(
    page_title="Enterprise AI Assistant",
    page_icon="AI",
    layout="wide",
)


@st.cache_resource(show_spinner=False)
def _get_graph():
    return build_graph()


def _render_sidebar():
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Open Page",
        ["Chat Assistant", "Implementation Dashboard"],
        index=0,
    )
    st.sidebar.markdown("### Runtime Snapshot")
    st.sidebar.caption(f"APP_ENV: `{Settings.APP_ENV}`")
    st.sidebar.caption(f"LLM_PROVIDER: `{Settings.resolved_llm_provider()}`")
    st.sidebar.caption(f"Vector: `{'Qdrant' if Settings.USE_CLOUD else 'FAISS'}`")
    st.sidebar.caption(f"Qdrant Collection: `{Settings.QDRANT_COLLECTION}`")
    return page


def main():
    graph = _get_graph()
    logger.info(
        "UI startup config | app_env=%s | use_cloud=%s | llm_provider=%s | qdrant_url_set=%s",
        Settings.APP_ENV,
        Settings.USE_CLOUD,
        Settings.resolved_llm_provider(),
        bool(Settings.QDRANT_URL),
    )

    apply_global_styles()
    selected_page = _render_sidebar()

    if selected_page == "Implementation Dashboard":
        render_implementation_dashboard(PROJECT_ROOT)
        return

    render_chat_page(graph, PROJECT_ROOT)


if __name__ == "__main__":
    main()
