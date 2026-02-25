from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
