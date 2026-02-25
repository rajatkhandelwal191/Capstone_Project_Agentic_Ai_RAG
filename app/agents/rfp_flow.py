from app.core.llm import get_llm
from pypdf import PdfReader
from app.core.logger import logger
import time

llm = get_llm()


def _read_pdf_text(file_path, max_chars=12000):
    if not file_path:
        return ""

    try:
        reader = PdfReader(file_path)
        chunks = []
        total = 0
        page_count = 0

        for page in reader.pages:
            page_count += 1
            page_text = (page.extract_text() or "").strip()
            if not page_text:
                continue
            chunks.append(page_text)
            total += len(page_text)
            if total >= max_chars:
                break

        return "\n\n".join(chunks)[:max_chars], page_count
    except Exception:
        return "", 0


def _should_use_uploaded_context(user_input: str, has_uploaded_file: bool) -> bool:
    if not has_uploaded_file:
        return False

    text = user_input.lower()
    doc_keywords = (
        "uploaded",
        "document",
        "pdf",
        "file",
        "summarize",
        "analyze",
        "this client proposal",
    )
    return any(keyword in text for keyword in doc_keywords)


def run_rfp_flow(state):
    request_id = getattr(state, "request_id", None) or "no-request-id"
    start = time.perf_counter()
    has_uploaded_file = bool(state.uploaded_file)
    use_uploaded_context = _should_use_uploaded_context(state.user_input, has_uploaded_file)
    rfp_text = ""
    page_count = 0

    logger.info(
        "request_id=%s | agent=rfp_flow | start | has_uploaded_file=%s | use_uploaded_context=%s",
        request_id,
        has_uploaded_file,
        use_uploaded_context,
    )

    if use_uploaded_context:
        rfp_text, page_count = _read_pdf_text(state.uploaded_file)
        logger.info(
            "request_id=%s | agent=rfp_flow | extracted_pdf | pages_read=%s | chars=%s",
            request_id,
            page_count,
            len(rfp_text),
        )

    prompt = f"""
You are an enterprise proposal writer.

Task:
- Draft a professional enterprise-style proposal response for the user request.
- If details are missing, make practical assumptions and include a short "Clarifications Needed" section.
- Keep output structured with headings and bullet points where useful.
- If expected output asks for enterprise-style proposal text, produce exactly that style.

Uploaded Document Context (use only when relevant):
{rfp_text if use_uploaded_context and rfp_text else "No uploaded document context used."}

User Request:
{state.user_input}
"""

    state.response = llm.invoke(prompt).content
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    logger.info(
        "request_id=%s | agent=rfp_flow | done | response_chars=%s | elapsed_ms=%.2f",
        request_id,
        len(state.response or ""),
        elapsed_ms,
    )
    return state
