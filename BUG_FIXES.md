# Bug Fixes Log

This file tracks bugs fixed in this project with short notes.

## 2026-02-25

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
