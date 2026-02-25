from app.core.llm import get_llm
from app.prompts.prompt_loader import load_prompts

prompts = load_prompts()
llm = get_llm()


TOOL_HINTS = (
    "incident",
    "incidents",
    "request",
    "requests",
    "service request",
    "service requests",
    "ticket",
    "tickets",
    "open incident",
    "open incidents",
    "open request",
    "open requests",
    "database",
    "status",
)

RFP_HINTS = (
    "rfp",
    "request for proposal",
    "proposal",
    "tender",
    "bid",
)


def _normalize_label(text: str) -> str:
    value = text.strip().upper()
    if "UPLOAD_FLOW" in value:
        return "UPLOAD_FLOW"
    if "TOOL_FLOW" in value or value == "TOOL":
        return "TOOL_FLOW"
    if "RFP_FLOW" in value or value == "RFP":
        return "RFP_FLOW"
    if "RAG_FLOW" in value or value == "RAG":
        return "RAG_FLOW"
    return "RAG_FLOW"


def classify_intent(user_input: str):
    text = user_input.lower().strip()
    has_tool_hint = any(hint in text for hint in TOOL_HINTS)
    has_rfp_hint = any(hint in text for hint in RFP_HINTS)

    # Deterministic routing for high-confidence user intents.
    if "upload" in text:
        return "UPLOAD_FLOW"
    if has_tool_hint and not has_rfp_hint:
        return "TOOL_FLOW"
    if has_rfp_hint and not has_tool_hint:
        return "RFP_FLOW"
    if not has_tool_hint and not has_rfp_hint:
        return "RAG_FLOW"

    prompt = f"""
{prompts['supervisor']}

User: {user_input}
"""

    result = llm.invoke(prompt).content
    return _normalize_label(result)
