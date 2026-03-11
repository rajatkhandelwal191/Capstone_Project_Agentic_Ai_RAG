import csv
import json
import uuid
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from app.core.config import Settings
from app.core.embeddings import get_embeddings
from app.core.logger import logger
from app.db.repository import get_incidents, get_service_requests
from app.rag.loaders import load_all_pdfs


def _record_to_document(record: Any, source: str, row_id: int) -> Document | None:
    if isinstance(record, dict):
        question = str(record.get("question", "")).strip()
        answer = str(record.get("answer", "")).strip()
        text = str(record.get("text") or record.get("content") or "").strip()

        if not text and question and answer:
            text = f"Question: {question}\nAnswer: {answer}"
        elif not text and question:
            text = f"Question: {question}"
        elif not text:
            text = "\n".join(
                f"{k}: {v}" for k, v in record.items() if v is not None and str(v).strip()
            ).strip()

        if not text:
            return None

        metadata = {
            "source": source,
            "source_type": "synthetic",
            "row_id": row_id,
            "upsert_key": f"synthetic:{source}:row:{row_id}",
        }
        if "id" in record:
            metadata["record_id"] = str(record["id"])
            metadata["upsert_key"] = f"synthetic:{source}:id:{metadata['record_id']}"
        return Document(page_content=text, metadata=metadata)

    text = str(record).strip()
    if not text:
        return None
    return Document(
        page_content=text,
        metadata={
            "source": source,
            "source_type": "synthetic",
            "row_id": row_id,
            "upsert_key": f"synthetic:{source}:row:{row_id}",
        },
    )


def _load_json_records(path: Path) -> list[Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    return [raw]


def _load_jsonl_records(path: Path) -> list[Any]:
    records: list[Any] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _load_csv_records(path: Path) -> list[Any]:
    records: list[Any] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return records


def _load_txt_records(path: Path) -> list[Any]:
    records: list[Any] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            text = line.strip()
            if text:
                records.append({"text": text})
    return records


def load_pdf_documents(folder: str) -> list[Document]:
    docs = load_all_pdfs(folder)
    normalized: list[Document] = []
    for doc in docs:
        metadata = dict(doc.metadata or {})
        source = str(metadata.get("source", "kb_pdf"))
        page = str(metadata.get("page", 0))
        metadata["source_type"] = "pdf"
        metadata["source"] = source
        metadata["upsert_key"] = f"pdf:{source}:page:{page}"
        normalized.append(Document(page_content=doc.page_content, metadata=metadata))
    logger.info("Loaded PDF docs | folder=%s | docs=%s", folder, len(normalized))
    return normalized


def load_synthetic_documents(path_str: str) -> list[Document]:
    path = Path(path_str)
    if not path.exists():
        logger.warning("Synthetic dataset file not found at %s. Skipping.", path)
        return []

    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        records = _load_jsonl_records(path)
    elif suffix == ".json":
        records = _load_json_records(path)
    elif suffix == ".csv":
        records = _load_csv_records(path)
    elif suffix == ".txt":
        records = _load_txt_records(path)
    else:
        raise ValueError(
            f"Unsupported synthetic dataset format: {suffix}. Use .jsonl, .json, .csv, or .txt"
        )

    docs: list[Document] = []
    for idx, record in enumerate(records, start=1):
        doc = _record_to_document(record, source=str(path), row_id=idx)
        if doc:
            docs.append(doc)

    logger.info("Loaded synthetic records | file=%s | records=%s", path, len(docs))
    return docs


def load_sqlite_documents() -> list[Document]:
    docs: list[Document] = []

    incidents = get_incidents()
    for incident in incidents:
        docs.append(
            Document(
                page_content=(
                    f"Incident ID: {incident.id}\n"
                    f"Title: {incident.title}\n"
                    f"Severity: {incident.severity}\n"
                    f"Team: {incident.team}\n"
                    f"Status: {incident.status}\n"
                    f"Created At: {incident.created_at}"
                ),
                metadata={
                    "source_type": "sqlite_incident",
                    "source": "sqlite:incidents",
                    "record_type": "incident",
                    "record_id": incident.id,
                    "status": incident.status,
                    "severity": incident.severity,
                    "team": incident.team,
                    "upsert_key": f"sqlite_incident:{incident.id}",
                },
            )
        )

    service_requests = get_service_requests()
    for request in service_requests:
        docs.append(
            Document(
                page_content=(
                    f"Service Request ID: {request.id}\n"
                    f"Department: {request.department}\n"
                    f"Request Type: {request.request_type}\n"
                    f"Status: {request.status}\n"
                    f"Created At: {request.created_at}"
                ),
                metadata={
                    "source_type": "sqlite_service_request",
                    "source": "sqlite:service_requests",
                    "record_type": "service_request",
                    "record_id": request.id,
                    "status": request.status,
                    "department": request.department,
                    "request_type": request.request_type,
                    "upsert_key": f"sqlite_service_request:{request.id}",
                },
            )
        )

    logger.info(
        "Loaded SQLite records | incidents=%s | service_requests=%s | total_docs=%s",
        len(incidents),
        len(service_requests),
        len(docs),
    )
    return docs


def _collection_exists(client: QdrantClient, collection_name: str) -> bool:
    collections = client.get_collections().collections
    return any(col.name == collection_name for col in collections)


def _ensure_collection(client: QdrantClient, collection_name: str, vector_size: int):
    if _collection_exists(client, collection_name):
        logger.info("Qdrant collection exists | collection=%s", collection_name)
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=qdrant_models.VectorParams(
            size=vector_size,
            distance=qdrant_models.Distance.COSINE,
        ),
    )
    logger.info(
        "Created Qdrant collection | collection=%s | vector_size=%s",
        collection_name,
        vector_size,
    )


def _refresh_source_types(client: QdrantClient, collection_name: str, source_types: set[str]):
    if not Settings.CLOUD_REFRESH_SOURCE_TYPES:
        return

    # Qdrant Cloud requires a payload index for filtered deletes on keyword fields.
    client.create_payload_index(
        collection_name=collection_name,
        field_name="source_type",
        field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
        wait=True,
    )

    for source_type in sorted(source_types):
        try:
            client.delete(
                collection_name=collection_name,
                points_selector=qdrant_models.FilterSelector(
                    filter=qdrant_models.Filter(
                        must=[
                            qdrant_models.FieldCondition(
                                key="source_type",
                                match=qdrant_models.MatchValue(value=source_type),
                            )
                        ]
                    )
                ),
                wait=True,
            )
            logger.info("Refreshed source_type in Qdrant | source_type=%s", source_type)
        except Exception as exc:
            logger.warning(
                "Could not refresh source_type=%s before upsert. Continuing with deterministic upsert only. | error=%s",
                source_type,
                exc,
            )


def _deterministic_point_id(upsert_key: str, chunk_index: int) -> str:
    key = f"{upsert_key}::chunk::{chunk_index}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def _build_points(chunks: list[Document], embeddings) -> list[qdrant_models.PointStruct]:
    if not chunks:
        return []

    texts = [doc.page_content for doc in chunks]
    vectors = embeddings.embed_documents(texts)

    per_doc_chunk_index: dict[str, int] = {}
    points: list[qdrant_models.PointStruct] = []
    for doc, vector in zip(chunks, vectors):
        metadata = dict(doc.metadata or {})
        upsert_key = str(metadata.get("upsert_key") or metadata.get("source") or "unknown")
        chunk_index = per_doc_chunk_index.get(upsert_key, 0)
        per_doc_chunk_index[upsert_key] = chunk_index + 1

        point_id = _deterministic_point_id(upsert_key, chunk_index)
        payload = dict(metadata)
        payload["chunk_index"] = chunk_index
        payload["text"] = doc.page_content

        points.append(
            qdrant_models.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        )

    return points


def _upsert_points(
    client: QdrantClient,
    collection_name: str,
    points: list[qdrant_models.PointStruct],
    batch_size: int = 64,
):
    for start in range(0, len(points), batch_size):
        batch = points[start : start + batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch,
            wait=True,
        )
    logger.info("Upserted points to Qdrant | collection=%s | points=%s", collection_name, len(points))


def ingest_to_qdrant():
    if not Settings.USE_CLOUD:
        raise RuntimeError("Set APP_ENV=cloud before running Qdrant ingestion.")

    Settings.ensure_cloud_vector_config()
    embeddings = get_embeddings()

    all_docs: list[Document] = []
    if Settings.INCLUDE_PDF_IN_INGEST:
        all_docs.extend(load_pdf_documents(Settings.KB_FOLDER))
    if Settings.INCLUDE_SYNTHETIC_IN_INGEST:
        all_docs.extend(load_synthetic_documents(Settings.SYNTHETIC_DATA_PATH))
    if Settings.INCLUDE_SQLITE_IN_INGEST:
        all_docs.extend(load_sqlite_documents())

    if not all_docs:
        raise RuntimeError(
            "No input documents found. Check kb_pdfs/, synthetic dataset path, and SQLite seed data."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(all_docs)
    if not chunks:
        raise RuntimeError("Document splitter produced zero chunks.")

    logger.info(
        "Prepared chunks for Qdrant ingestion | source_docs=%s | chunks=%s",
        len(all_docs),
        len(chunks),
    )

    vector_size = Settings.EMBED_DIM
    try:
        probe_vector = embeddings.embed_query("vector-size-probe")
        vector_size = len(probe_vector)
    except Exception as exc:
        logger.warning(
            "Embedding size probe failed. Using EMBED_DIM=%s | error=%s",
            Settings.EMBED_DIM,
            exc,
        )

    client = QdrantClient(
        url=Settings.QDRANT_URL,
        api_key=Settings.QDRANT_API_KEY,
        timeout=60,
    )
    _ensure_collection(client, Settings.QDRANT_COLLECTION, vector_size)

    source_types = {
        str(doc.metadata.get("source_type", "unknown"))
        for doc in chunks
        if doc.metadata
    }
    _refresh_source_types(client, Settings.QDRANT_COLLECTION, source_types)

    points = _build_points(chunks, embeddings)
    _upsert_points(client, Settings.QDRANT_COLLECTION, points)
    logger.info(
        "Qdrant ingestion complete | collection=%s | source_types=%s | uploaded_chunks=%s",
        Settings.QDRANT_COLLECTION,
        sorted(source_types),
        len(points),
    )


if __name__ == "__main__":
    ingest_to_qdrant()
