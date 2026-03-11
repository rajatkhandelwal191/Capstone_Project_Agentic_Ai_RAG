from dotenv import load_dotenv
import os

load_dotenv()


def _as_bool(name: str, default: str = "false") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


class Settings:
    APP_ENV = os.getenv("APP_ENV", "local").strip().lower()
    USE_CLOUD = APP_ENV == "cloud"

    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    LOCAL_EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
    GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

    QDRANT_URL = os.getenv("QDRANT_URL", "").strip()
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "").strip()
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "capstone_kb").strip()

    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))
    LOCAL_FAISS_PATH = os.getenv("LOCAL_FAISS_PATH", "app/rag/faiss_index")
    KB_FOLDER = os.getenv("KB_FOLDER", "kb_pdfs")
    SYNTHETIC_DATA_PATH = os.getenv("SYNTHETIC_DATA_PATH", "data/synthetic_dataset.jsonl")
    EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))
    INCLUDE_PDF_IN_INGEST = _as_bool("INCLUDE_PDF_IN_INGEST", "true")
    INCLUDE_SYNTHETIC_IN_INGEST = _as_bool("INCLUDE_SYNTHETIC_IN_INGEST", "true")
    INCLUDE_SQLITE_IN_INGEST = _as_bool("INCLUDE_SQLITE_IN_INGEST", "true")
    CLOUD_REFRESH_SOURCE_TYPES = _as_bool("CLOUD_REFRESH_SOURCE_TYPES", "true")

    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

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
