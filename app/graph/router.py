from app.core.llm import get_llm
from app.prompts.prompt_loader import load_prompts
from app.core.logger import logger
import re

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
    "draft proposal",
    "bid response",
    "rfp response",
    "propose solution",
    "client requirement",
    "cloud migration",
    "high availability system",
    "scalable architecture",
)

EXPLICIT_UPLOAD_HINTS = (
    "i want to upload",
    "upload an rfp",
    "upload rfp",
    "upload pdf",
    "upload file",
)

UPLOADED_DOC_ACTION_HINTS = (
    "summarize my uploaded document",
    "summarize uploaded document",
    "summarize my uploaded file",
    "summarize my uploaded pdf",
    "summarize uploaded pdf",
    "analyze this client proposal",
    "analyze uploaded document",
    "analyze uploaded file",
    "analyze uploaded pdf",
    "uploaded document",
    "uploaded file",
    "uploaded pdf",
    "this client proposal",
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


def classify_intent(user_input: str, has_uploaded_file: bool = False):
    text = user_input.lower().strip()
    matched_tool_hints = [hint for hint in TOOL_HINTS if hint in text]
    matched_rfp_hints = [hint for hint in RFP_HINTS if hint in text]
    matched_explicit_upload_hints = [hint for hint in EXPLICIT_UPLOAD_HINTS if hint in text]
    matched_uploaded_doc_action_hints = [hint for hint in UPLOADED_DOC_ACTION_HINTS if hint in text]

    has_tool_hint = bool(matched_tool_hints)
    has_rfp_hint = bool(matched_rfp_hints)
    has_explicit_upload_hint = bool(matched_explicit_upload_hints)
    has_uploaded_doc_action_hint = bool(matched_uploaded_doc_action_hints)

    logger.info(
        "Intent classifier inputs | text=%s | has_uploaded_file=%s | tool_hints=%s | rfp_hints=%s | explicit_upload_hints=%s | uploaded_doc_hints=%s",
        text,
        has_uploaded_file,
        matched_tool_hints[:3],
        matched_rfp_hints[:3],
        matched_explicit_upload_hints[:3],
        matched_uploaded_doc_action_hints[:3],
    )

    # Deterministic routing for high-confidence user intents.
    has_upload_word = bool(re.search(r"\bupload\b", text))
    if has_explicit_upload_hint or has_upload_word:
        logger.info("Intent classified deterministically | route=UPLOAD_FLOW | reason=explicit_upload_request")
        return "UPLOAD_FLOW"
    if has_uploaded_doc_action_hint and not has_uploaded_file:
        logger.info("Intent classified deterministically | route=UPLOAD_FLOW | reason=doc_action_without_uploaded_file")
        return "UPLOAD_FLOW"
    if has_uploaded_doc_action_hint and has_uploaded_file:
        logger.info("Intent classified deterministically | route=RFP_FLOW | reason=doc_action_with_uploaded_file")
        return "RFP_FLOW"
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
HasUploadedFile: {"yes" if has_uploaded_file else "no"}
"""

    result = llm.invoke(prompt).content
    normalized = _normalize_label(result)
    logger.info(
        "Intent classified by LLM | raw=%s | normalized=%s",
        result.strip(),
        normalized,
    )
    return normalized
