from app.rag.retriever import query_rag
from app.core.llm import get_llm

llm = get_llm()

def run_rag_flow(state):

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
    return state