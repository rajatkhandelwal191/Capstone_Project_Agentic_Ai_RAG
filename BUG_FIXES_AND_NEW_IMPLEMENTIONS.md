# Bug Fixes and New Implementions

This file tracks bug fixes and new implementations in this project with short notes.

## 2026-02-25

### Bug Fixes

- Fixed package/interpreter mismatch: project dependencies worked in Poetry env but not global Python.
- Fixed module execution issues by running app modules with `python -m ...` instead of file paths.
- Fixed Streamlit import root issue for `app.*` modules by ensuring project root is added to `sys.path`.
- Fixed deprecated/broken LangChain imports:
  - `langchain.vectorstores` -> `langchain_community.vectorstores`
  - `langchain.embeddings.OllamaEmbeddings` -> `langchain_ollama.OllamaEmbeddings`
  - `langchain.text_splitter` -> `langchain_text_splitters`
- Fixed SQLite seed failure (`datatype mismatch`) by recreating DB with text IDs matching seeded values.
- Fixed Ollama runtime 404 by aligning configured model with installed model (`llama3.2:latest`).
- Fixed LangGraph output handling in Streamlit (`dict` vs attribute access) for `needs_upload` and `response`.
- Fixed intent routing that incorrectly sent operational queries to RFP flow.
- Fixed schema mismatch in Pydantic models (`Incident.id` / `ServiceRequest.id`) from `int` to `str`.
- Fixed tool flow for request queries:
  - Added service request repository/tool functions.
  - Added routing hints for `request`/`requests`.
  - Added `show open requests` support using DB-backed open service requests output.
- Fixed chat UX delay where user messages only appeared after assistant response:
  - Rendered user chat bubble immediately on submit in `app/ui/streamlit_app.py`.
- Fixed RFP upload UX where uploader disappeared before file selection:
  - Moved uploader to persistent session-driven UI state (`awaiting_upload`) in `app/ui/streamlit_app.py`.
- Fixed RFP flow not using uploaded file:
  - Wired uploaded file path from Streamlit session into graph state.
  - Added PDF text extraction in `app/agents/rfp_flow.py` and included extracted content in the RFP prompt.
  - Added guard response when RFP flow is called before upload.
- Fixed missing backend visibility in terminal while using Streamlit:
  - Added explicit stdout logger setup in `app/core/logger.py`.
  - Added request, routing, and flow lifecycle logs across UI/graph/agent layers.
- Enhanced backend trace detail for easier debugging:
  - Added per-request IDs, node/agent dispatch logs, intent classifier reasoning, selected tool names, retriever metrics, and elapsed timing in terminal logs.
  - Added assistant response preview logging in Streamlit so AI reply text appears in terminal logs.
- Redesigned RFP vs Upload intent flow:
  - RFP drafting prompts now route to `RFP_FLOW` and generate enterprise-style responses without forcing PDF upload.
  - Upload UI is shown only for explicit upload requests and uploaded-document actions when no file exists.
  - Uploaded-document actions (`summarize/analyze uploaded ...`) route to `RFP_FLOW` once a file is present.

### New Implementations

- Added Mermaid graph flow support for architecture documentation:
  - Added export script at `app/graph/export_mermaid.py`.
  - Generated graph source at `docs/graph_flow.mmd`.
  - Added Mermaid visualization section in `README.md`.
