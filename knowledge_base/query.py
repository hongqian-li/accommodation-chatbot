import os
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "hamk_accommodation"
TOP_K = 3


def get_context(query: str) -> str:
    client = chromadb.PersistentClient(path=os.path.abspath(CHROMA_PATH))
    embedding_fn = DefaultEmbeddingFunction()

    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    results = collection.query(
        query_texts=[query],
        n_results=TOP_K,
    )

    chunks = results["documents"][0]
    context = "\n\n---\n\n".join(chunks)
    return context


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What room types are available at Evo campus?"
    print(f"Query: {query}\n")
    context = get_context(query)
    print("Top relevant chunks:\n")
    print(context)
