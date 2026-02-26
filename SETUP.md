# Setup Guide

This guide explains how to set up and run the project after cloning from GitHub, including how to test each flow.

## 1. Prerequisites

- Python `3.12` to `<3.15`
- Poetry installed
- Ollama installed and running

## 2. Clone And Open In Terminal

```powershell
git clone <your-repo-url>
cd Capstone_Project_Agentic_Ai_RAG
```

## 3. Install Python Dependencies (Poetry)

```powershell
poetry install
```

## 4. Configure Environment Variables

Create `.env` in project root:

```env
OLLAMA_MODEL=llama3.2:latest
EMBED_MODEL=nomic-embed-text
TEMPERATURE=0.2
```

## 5. Prepare Ollama Models

In a new terminal:

```powershell
ollama pull llama3.2:latest
ollama pull nomic-embed-text
ollama serve
```

If `ollama serve` is already running, keep it running and skip restarting.

## 6. Initialize Local Database (Tool Flow Data)

Run these from project root:

```powershell
poetry run python -m app.db.init_db
poetry run python -m app.db.seed_db
```

Files used:
- `app/db/init_db.py`
- `app/db/seed_db.py`
- DB output: `app/db/database.db`

## 7. Build RAG Vector Index

Put your knowledge PDFs in `kb_pdfs/`, then run:

```powershell
poetry run python -m app.rag.build_index
```

Files used:
- `app/rag/build_index.py`
- `app/rag/loaders.py`
- Index output: `app/rag/faiss_index/`

## 8. Run The App (Streamlit UI)

```powershell
poetry run streamlit run app/ui/streamlit_app.py
```

Open the URL shown in terminal (usually `http://localhost:8501`).

## 9. How To Test Each Flow

### A) TOOL_FLOW (Incidents/Requests from SQLite)

Try:
- `show open incidents`
- `show open requests`

Expected:
- Returns rows from seeded DB data.

### B) RAG_FLOW (Knowledge Base Q&A from PDFs)

Try:
- `What services does the company provide?`
- `Summarize the SLA expectations`

Expected:
- Answers based on documents indexed from `kb_pdfs/`.

### C) RFP_FLOW (Enterprise Proposal Generation, no upload required)

Try:
- `Draft proposal for cloud migration`
- `Create bid response for high availability system`
- `Write RFP response for scalable architecture`
- `Summarize this client requirement and propose solution`

Expected:
- Enterprise-style proposal response.
- If details are missing, model may add clarifications/assumptions.

### D) UPLOAD_FLOW (Only when upload/document-analysis intent is detected)

Try:
- `I want to upload an RFP`
- `Summarize my uploaded document`
- `Analyze this client proposal`

Expected:
- Upload control appears when needed.
- After upload, uploaded-document prompts are processed with uploaded PDF context.

## 10. Useful Developer Commands

Regenerate Mermaid graph:

```powershell
poetry run python -m app.graph.export_mermaid
```

Quick syntax check:

```powershell
python -m py_compile app\ui\streamlit_app.py
```

## 11. Common Issues

- `ModuleNotFoundError` for project packages:
  - Use `poetry run ...` commands instead of global Python.
- Ollama model not found / 404:
  - Run `ollama pull llama3.2:latest` and keep `ollama serve` running.
- RAG not answering properly:
  - Ensure PDFs exist in `kb_pdfs/` and rebuild index.
- Tool flow returns empty:
  - Re-run DB init + seed commands.
