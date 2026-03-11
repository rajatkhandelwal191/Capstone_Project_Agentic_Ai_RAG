from app.core.config import Settings


def get_llm():
    provider = Settings.resolved_llm_provider()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        Settings.ensure_cloud_llm_config()
        return ChatGoogleGenerativeAI(
            model=Settings.GEMINI_CHAT_MODEL,
            temperature=Settings.TEMPERATURE,
            google_api_key=Settings.GOOGLE_API_KEY,
        )

    if provider == "groq":
        from langchain_groq import ChatGroq

        Settings.ensure_groq_config()
        return ChatGroq(
            model=Settings.GROQ_MODEL,
            temperature=Settings.TEMPERATURE,
            groq_api_key=Settings.GROQ_API_KEY,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=Settings.OLLAMA_MODEL,
            temperature=Settings.TEMPERATURE,
        )

    raise ValueError(
        f"Unsupported LLM provider '{provider}'. "
        "Use one of: auto, gemini, groq, ollama."
    )
