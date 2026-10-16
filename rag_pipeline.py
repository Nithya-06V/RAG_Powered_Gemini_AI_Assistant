import uuid

import chromadb

from document_processor import extract_pages, split_pages
from gemini_service import embed_texts


def get_collection(app):
    client = chromadb.PersistentClient(path=str(app.config["VECTOR_STORE_PATH"]))
    return client.get_or_create_collection(
        name="uploaded_documents",
        metadata={"hnsw:space": "cosine"},
    )


def index_file(app, document_id, user_id, filename, file_path):
    chunks = split_pages(extract_pages(file_path))
    if not chunks:
        raise ValueError("No text chunks could be created from this document.")
    collection = get_collection(app)
    vectors = []
    for batch_start in range(0, len(chunks), 50):
        batch = chunks[batch_start : batch_start + 50]
        vectors.extend(embed_texts([chunk["text"] for chunk in batch], "RETRIEVAL_DOCUMENT"))
    metadatas = [
        {
            "document_id": document_id,
            "user_id": user_id,
            "filename": filename,
            "chunk": index + 1,
            "page": chunk["page"] or 0,
        }
        for index, chunk in enumerate(chunks)
    ]
    collection.add(
        ids=[f"{document_id}-{index}-{uuid.uuid4().hex[:8]}" for index in range(len(chunks))],
        documents=[chunk["text"] for chunk in chunks],
        embeddings=vectors,
        metadatas=metadatas,
    )
    return len(chunks)


def retrieve(app, user_id, question, limit=5):
    collection = get_collection(app)
    if collection.count() == 0:
        return []
    query_vector = embed_texts([question], "RETRIEVAL_QUERY")[0]
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(limit, collection.count()),
        where={"user_id": user_id},
        include=["documents", "metadatas", "distances"],
    )
    matches = []
    for text, metadata, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        if distance <= 0.78:
            matches.append({"text": text, "metadata": metadata, "distance": distance})
    return matches


def remove_document(app, document_id):
    collection = get_collection(app)
    collection.delete(where={"document_id": document_id})
