from app.core.config import Settings


def get_embeddings():
    if Settings.USE_CLOUD:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        Settings.ensure_cloud_llm_config()
        return GoogleGenerativeAIEmbeddings(
            model=Settings.GEMINI_EMBED_MODEL,
            google_api_key=Settings.GOOGLE_API_KEY,
        )

    from langchain_ollama import OllamaEmbeddings

    return OllamaEmbeddings(model=Settings.LOCAL_EMBED_MODEL)
