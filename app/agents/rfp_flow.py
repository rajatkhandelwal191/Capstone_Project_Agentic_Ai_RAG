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


def run_rfp_flow(state):
    request_id = getattr(state, "request_id", None) or "no-request-id"
    start = time.perf_counter()
    if not state.uploaded_file:
        state.needs_upload = True
        state.response = "Please upload your RFP PDF first, then ask your RFP question."
        logger.info("request_id=%s | agent=rfp_flow | blocked | reason=no_uploaded_file", request_id)
        return state

    logger.info("request_id=%s | agent=rfp_flow | start | file=%s", request_id, state.uploaded_file)
    rfp_text, page_count = _read_pdf_text(state.uploaded_file)
    logger.info(
        "request_id=%s | agent=rfp_flow | extracted_pdf | pages_read=%s | chars=%s",
        request_id,
        page_count,
        len(rfp_text),
    )

    prompt = f"""
You are drafting an enterprise RFP response.

RFP Document Content:
{rfp_text if rfp_text else "No readable content found in the uploaded file."}

User Request:
{state.user_input}

Return a concise, professional response with clear sections and actionable details.
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
