from app.core.llm import get_llm

llm = get_llm()

def run_rfp_flow(state):

    prompt = f"""
Draft an enterprise RFP response for:

{state.user_input}
"""

    state.response = llm.invoke(prompt).content
    return state