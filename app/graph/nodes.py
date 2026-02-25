from app.graph.router import classify_intent
from app.agents.rag_flow import run_rag_flow
from app.agents.tool_flow import run_tool_flow
from app.agents.rfp_flow import run_rfp_flow
from app.core.logger import logger

def _rid(state):
    return getattr(state, "request_id", None) or "no-request-id"


def supervisor_node(state):
    logger.info("request_id=%s | node=supervisor | enter", _rid(state))

    state.intent = classify_intent(state.user_input)
    logger.info(
        "request_id=%s | node=supervisor | exit | routed_intent=%s",
        _rid(state),
        state.intent,
    )
    return state


def rag_node(state):
    logger.info("request_id=%s | node=rag | dispatch_agent=run_rag_flow", _rid(state))
    return run_rag_flow(state)


def tool_node(state):
    logger.info("request_id=%s | node=tool | dispatch_agent=run_tool_flow", _rid(state))
    return run_tool_flow(state)

def upload_node(state):
    logger.info("request_id=%s | node=upload | enter", _rid(state))

    state.needs_upload = True
    state.response = "Please upload your RFP PDF."
    logger.info("request_id=%s | node=upload | exit | needs_upload=True", _rid(state))

    return state


def rfp_node(state):
    logger.info("request_id=%s | node=rfp | dispatch_agent=run_rfp_flow", _rid(state))
    return run_rfp_flow(state)
