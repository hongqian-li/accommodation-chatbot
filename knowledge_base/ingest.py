import os
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "hamk_accommodation.txt")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "hamk_accommodation"

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def load_text(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def ingest():
    print(f"Loading text from: {DATA_FILE}")
    text = load_text(DATA_FILE)

    chunks = split_into_chunks(text)
    print(f"Split into {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    client = chromadb.PersistentClient(path=os.path.abspath(CHROMA_PATH))
    embedding_fn = DefaultEmbeddingFunction()

    # Reset collection if it already exists to avoid duplicate inserts
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print(f"Existing collection '{COLLECTION_NAME}' cleared.")

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)

    print(f"Stored {len(chunks)} chunks in ChromaDB at '{os.path.abspath(CHROMA_PATH)}'")
    print("Ingestion complete.")


if __name__ == "__main__":
    ingest()
