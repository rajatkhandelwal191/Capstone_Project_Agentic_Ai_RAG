from app.core.config import Settings


def get_llm():
    if Settings.USE_CLOUD:
        from langchain_google_genai import ChatGoogleGenerativeAI

        Settings.ensure_cloud_llm_config()
        return ChatGoogleGenerativeAI(
            model=Settings.GEMINI_CHAT_MODEL,
            temperature=Settings.TEMPERATURE,
            google_api_key=Settings.GOOGLE_API_KEY,
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=Settings.OLLAMA_MODEL,
        temperature=Settings.TEMPERATURE,
    )
