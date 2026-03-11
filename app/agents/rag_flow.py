from app.rag.retriever import query_rag
from app.core.llm import get_llm
from app.core.logger import logger
import time

llm = get_llm()


def _friendly_llm_error(exc: Exception) -> str:
    text = str(exc)
    if "ResourceExhausted" in text or "429" in text or "quota" in text.lower():
        return (
            "Gemini API quota is exhausted (HTTP 429). "
            "Please wait and retry, or switch to APP_ENV=local to use Ollama."
        )
    return "The language model is currently unavailable. Please retry shortly."

def run_rag_flow(state):
    request_id = getattr(state, "request_id", None) or "no-request-id"
    logger.info("request_id=%s | agent=rag_flow | start", request_id)
    start = time.perf_counter()

    try:
        context = query_rag(state.user_input)
    except Exception as exc:
        logger.exception("request_id=%s | agent=rag_flow | retrieval_failed | error=%s", request_id, exc)
        state.response = (
            "I could not access the knowledge index. "
            "Check your retrieval backend configuration and ingestion state."
        )
        return state

    logger.info(
        "request_id=%s | agent=rag_flow | context_chars=%s",
        request_id,
        len(context),
    )

    prompt = f"""
Answer using ONLY the context below.

Context:
{context}

Question:
{state.user_input}
"""

    try:
        response = llm.invoke(prompt).content
    except Exception as exc:
        logger.exception("request_id=%s | agent=rag_flow | llm_failed | error=%s", request_id, exc)
        state.response = _friendly_llm_error(exc)
        return state

    state.response = response
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    logger.info(
        "request_id=%s | agent=rag_flow | done | response_chars=%s | elapsed_ms=%.2f",
        request_id,
        len(response or ""),
        elapsed_ms,
    )
    return state
