from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import *
from app.core.logger import logger

def build_graph():

    workflow = StateGraph(GraphState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("tool", tool_node)
    workflow.add_node("rfp", rfp_node)
    workflow.add_node("upload", upload_node)


    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state.intent,
        {
            "RAG_FLOW": "rag",
            "TOOL_FLOW": "tool",
            "RFP_FLOW": "rfp",
            "UPLOAD_FLOW":"upload"

        }
    )

    workflow.add_edge("rag", END)
    workflow.add_edge("tool", END)
    workflow.add_edge("rfp", END)
    workflow.add_edge("upload", END)

    logger.info(
        "Graph topology initialized | entry=supervisor | routes={RAG_FLOW:rag, TOOL_FLOW:tool, RFP_FLOW:rfp, UPLOAD_FLOW:upload}"
    )
    return workflow.compile()
