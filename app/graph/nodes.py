from app.graph.router import classify_intent
from app.agents.rag_flow import run_rag_flow
from app.agents.tool_flow import run_tool_flow
from app.agents.rfp_flow import run_rfp_flow

def supervisor_node(state):

    state.intent = classify_intent(state.user_input)
    return state


def rag_node(state):
    return run_rag_flow(state)


def tool_node(state):
    return run_tool_flow(state)

def upload_node(state):

    state.needs_upload = True
    state.response = "Please upload your RFP PDF."

    return state


def rfp_node(state):
    return run_rfp_flow(state)