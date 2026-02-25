from app.core.llm import get_llm
from app.prompts.prompt_loader import load_prompts
from app.core.logger import logger

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
    matched_tool_hints = [hint for hint in TOOL_HINTS if hint in text]
    matched_rfp_hints = [hint for hint in RFP_HINTS if hint in text]
    has_tool_hint = bool(matched_tool_hints)
    has_rfp_hint = bool(matched_rfp_hints)

    logger.info(
        "Intent classifier inputs | text=%s | tool_hints=%s | rfp_hints=%s",
        text,
        matched_tool_hints[:3],
        matched_rfp_hints[:3],
    )

    # Deterministic routing for high-confidence user intents.
    if "upload" in text:
        logger.info("Intent classified deterministically | route=UPLOAD_FLOW | reason=keyword_upload")
        return "UPLOAD_FLOW"
    if has_tool_hint and not has_rfp_hint:
        logger.info("Intent classified deterministically | route=TOOL_FLOW | reason=tool_hints_only")
        return "TOOL_FLOW"
    if has_rfp_hint and not has_tool_hint:
        logger.info("Intent classified deterministically | route=RFP_FLOW | reason=rfp_hints_only")
        return "RFP_FLOW"
    if not has_tool_hint and not has_rfp_hint:
        logger.info("Intent classified deterministically | route=RAG_FLOW | reason=no_hints")
        return "RAG_FLOW"

    prompt = f"""
{prompts['supervisor']}

User: {user_input}
"""

    result = llm.invoke(prompt).content
    normalized = _normalize_label(result)
    logger.info(
        "Intent classified by LLM | raw=%s | normalized=%s",
        result.strip(),
        normalized,
    )
    return normalized
