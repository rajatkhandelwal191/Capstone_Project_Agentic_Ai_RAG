from app.graph.router import classify_intent
from app.agents.rag_flow import run_rag_flow
from app.agents.tool_flow import run_tool_flow
from app.agents.rfp_flow import run_rfp_flow
from app.core.logger import logger

def supervisor_node(state):

    state.intent = classify_intent(state.user_input)
    logger.info("Routed intent=%s", state.intent)
    return state


def rag_node(state):
    logger.info("Running RAG flow")
    return run_rag_flow(state)


def tool_node(state):
    logger.info("Running TOOL flow")
    return run_tool_flow(state)

def upload_node(state):
    logger.info("Running UPLOAD flow")

    state.needs_upload = True
    state.response = "Please upload your RFP PDF."

    return state


def rfp_node(state):
    logger.info("Running RFP flow")
    return run_rfp_flow(state)
