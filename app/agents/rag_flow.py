from app.rag.retriever import query_rag
from app.core.llm import get_llm
from app.core.logger import logger
import time

llm = get_llm()

def run_rag_flow(state):
    request_id = getattr(state, "request_id", None) or "no-request-id"
    logger.info("request_id=%s | agent=rag_flow | start", request_id)
    start = time.perf_counter()

    context = query_rag(state.user_input)
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

    response = llm.invoke(prompt).content

    state.response = response
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    logger.info(
        "request_id=%s | agent=rag_flow | done | response_chars=%s | elapsed_ms=%.2f",
        request_id,
        len(response or ""),
        elapsed_ms,
    )
    return state
