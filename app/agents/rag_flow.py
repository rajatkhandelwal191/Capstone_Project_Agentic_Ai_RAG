from app.rag.retriever import query_rag
from app.core.llm import get_llm
from app.core.logger import logger

llm = get_llm()

def run_rag_flow(state):
    logger.info("RAG query started")

    context = query_rag(state.user_input)

    prompt = f"""
Answer using ONLY the context below.

Context:
{context}

Question:
{state.user_input}
"""

    response = llm.invoke(prompt).content

    state.response = response
    logger.info("RAG query completed")
    return state
