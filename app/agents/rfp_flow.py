from app.core.llm import get_llm
from pypdf import PdfReader
from app.core.logger import logger

llm = get_llm()


def _read_pdf_text(file_path, max_chars=12000):
    if not file_path:
        return ""

    try:
        reader = PdfReader(file_path)
        chunks = []
        total = 0

        for page in reader.pages:
            page_text = (page.extract_text() or "").strip()
            if not page_text:
                continue
            chunks.append(page_text)
            total += len(page_text)
            if total >= max_chars:
                break

        return "\n\n".join(chunks)[:max_chars]
    except Exception:
        return ""


def run_rfp_flow(state):
    if not state.uploaded_file:
        state.needs_upload = True
        state.response = "Please upload your RFP PDF first, then ask your RFP question."
        logger.info("RFP flow blocked: no uploaded file present")
        return state

    logger.info("RFP flow started with file: %s", state.uploaded_file)
    rfp_text = _read_pdf_text(state.uploaded_file)

    prompt = f"""
You are drafting an enterprise RFP response.

RFP Document Content:
{rfp_text if rfp_text else "No readable content found in the uploaded file."}

User Request:
{state.user_input}

Return a concise, professional response with clear sections and actionable details.
"""

    state.response = llm.invoke(prompt).content
    logger.info("RFP flow completed")
    return state
