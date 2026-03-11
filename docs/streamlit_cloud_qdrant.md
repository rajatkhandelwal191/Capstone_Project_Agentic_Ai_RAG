# Streamlit Cloud + Gemini + Qdrant

This guide explains how to deploy the app for free on Streamlit Community Cloud using Gemini and Qdrant Cloud.

## 1. Security First

- If an API key was exposed publicly, rotate it immediately.
- Never commit keys in `.env` or code.
- Use Streamlit Cloud Secrets for production.

## 2. Environment Switch

The app now supports two modes through `APP_ENV`:

- `APP_ENV=local`:
  - uses local `Ollama` + local `FAISS`.
- `APP_ENV=cloud`:
  - uses `Gemini` + `Qdrant Cloud`.

See `.env.example` for all variables.

## 3. Where To Keep Synthetic Dataset

Recommended pattern:

1. Keep raw synthetic dataset in your repo or private storage as source-of-truth.
2. In this project, default path is:
   - `data/synthetic_dataset.jsonl`
3. Ingest that dataset into Qdrant once using the ingestion command.
4. Runtime queries read vectors from Qdrant, not from local files.

Qdrant stores:
- vector embeddings
- payload metadata (text/source/IDs) per point

## 4. Dataset Format

Supported formats for ingestion:

- `.jsonl`
- `.json`
- `.csv`
- `.txt`

For `.jsonl`, common keys such as `text`, `content`, `question`, `answer` are handled automatically.

Sample file:
- `data/synthetic_dataset.sample.jsonl`

## 5. One-Time Qdrant Ingestion

Set cloud env vars (`APP_ENV=cloud`, Gemini and Qdrant keys), then run:

```powershell
poetry run python -m app.rag.ingest_qdrant
```

What this does:

1. Loads PDFs from `kb_pdfs/`
2. Loads synthetic dataset from `SYNTHETIC_DATA_PATH`
3. Loads SQLite seed data from `incidents` and `service_requests`
4. Chunks documents
5. Creates Qdrant collection if missing
6. Upserts vectors + payloads with deterministic point IDs

Deterministic IDs are generated from source record keys + chunk index so reruns do true upsert without duplicate points. By default, the ingestor also refreshes source types before upsert (`CLOUD_REFRESH_SOURCE_TYPES=true`) to prevent stale chunks.

## 6. Deploy To Streamlit Community Cloud

1. Push this repo to GitHub.
2. In Streamlit Community Cloud, create app from that repo.
3. Entrypoint:
   - `app/ui/streamlit_app.py`
4. In app Secrets, add:

```toml
APP_ENV="cloud"
GOOGLE_API_KEY="your_rotated_key"
GEMINI_CHAT_MODEL="gemini-2.0-flash"
GEMINI_EMBED_MODEL="gemini-embedding-001"
QDRANT_URL="https://<your-cluster-url>"
QDRANT_API_KEY="<your-qdrant-api-key>"
QDRANT_COLLECTION="capstone_kb"
RAG_TOP_K="4"
SYNTHETIC_DATA_PATH="data/synthetic_dataset.jsonl"
```

5. Redeploy.

## 7. Local Development

For local mode:

```env
APP_ENV=local
OLLAMA_MODEL=llama3.2:latest
EMBED_MODEL=nomic-embed-text
LOCAL_FAISS_PATH=app/rag/faiss_index
```

Build local FAISS index:

```powershell
poetry run python -m app.rag.build_index
```

Run app:

```powershell
poetry run streamlit run app/ui/streamlit_app.py
```
