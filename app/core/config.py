from dotenv import load_dotenv
import os

load_dotenv()


def _get_streamlit_secret(name: str):
    try:
        import streamlit as st

        if name in st.secrets:
            value = st.secrets[name]
            if value is None:
                return None
            return str(value)
    except Exception:
        return None
    return None


def _get(name: str, default: str | None = None):
    env_value = os.getenv(name)
    if env_value is not None and env_value != "":
        return env_value

    secret_value = _get_streamlit_secret(name)
    if secret_value is not None and secret_value != "":
        return secret_value

    return default


def _as_bool(name: str, default: str = "false") -> bool:
    value = str(_get(name, default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


class Settings:
    APP_ENV = str(_get("APP_ENV", "local")).strip().lower()
    USE_CLOUD = APP_ENV == "cloud"

    OLLAMA_MODEL = str(_get("OLLAMA_MODEL", "llama3.2:latest"))
    LOCAL_EMBED_MODEL = str(_get("EMBED_MODEL", "nomic-embed-text"))

    GOOGLE_API_KEY = _get("GOOGLE_API_KEY") or _get("GEMINI_API_KEY")
    GEMINI_CHAT_MODEL = str(_get("GEMINI_CHAT_MODEL", "gemini-2.0-flash"))
    GEMINI_EMBED_MODEL = str(_get("GEMINI_EMBED_MODEL", "gemini-embedding-001"))

    QDRANT_URL = str(_get("QDRANT_URL", "")).strip()
    QDRANT_API_KEY = str(_get("QDRANT_API_KEY", "")).strip()
    QDRANT_COLLECTION = str(_get("QDRANT_COLLECTION", "capstone_kb")).strip()

    RAG_TOP_K = int(str(_get("RAG_TOP_K", "4")))
    LOCAL_FAISS_PATH = str(_get("LOCAL_FAISS_PATH", "app/rag/faiss_index"))
    KB_FOLDER = str(_get("KB_FOLDER", "kb_pdfs"))
    SYNTHETIC_DATA_PATH = str(_get("SYNTHETIC_DATA_PATH", "data/synthetic_dataset.jsonl"))
    EMBED_DIM = int(str(_get("EMBED_DIM", "768")))
    INCLUDE_PDF_IN_INGEST = _as_bool("INCLUDE_PDF_IN_INGEST", "true")
    INCLUDE_SYNTHETIC_IN_INGEST = _as_bool("INCLUDE_SYNTHETIC_IN_INGEST", "true")
    INCLUDE_SQLITE_IN_INGEST = _as_bool("INCLUDE_SQLITE_IN_INGEST", "true")
    CLOUD_REFRESH_SOURCE_TYPES = _as_bool("CLOUD_REFRESH_SOURCE_TYPES", "true")

    TEMPERATURE = float(str(_get("TEMPERATURE", "0.2")))

    @classmethod
    def ensure_cloud_llm_config(cls):
        if not cls.GOOGLE_API_KEY:
            raise ValueError("Missing GOOGLE_API_KEY (or GEMINI_API_KEY) for APP_ENV=cloud.")

    @classmethod
    def ensure_cloud_vector_config(cls):
        cls.ensure_cloud_llm_config()
        if not cls.QDRANT_URL:
            raise ValueError("Missing QDRANT_URL for APP_ENV=cloud.")
        if not cls.QDRANT_API_KEY:
            raise ValueError("Missing QDRANT_API_KEY for APP_ENV=cloud.")
