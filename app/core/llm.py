from langchain_ollama import ChatOllama
from app.core.config import Settings


def get_llm():
    return ChatOllama(
        model=Settings.MODEL,
        temperature=Settings.TEMPERATURE,
    )
