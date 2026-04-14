import os
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
COLLECTION_NAME = "hamk_accommodation"
TOP_K = 3

# Average L2 distance threshold above which web search fallback is triggered.
# Calibrated on the hamk_accommodation ChromaDB collection
# (DefaultEmbeddingFunction, L2 space):
#   KB-matched queries (e.g. "rooms at Evo") → avg dist ~0.72–0.92
#   Off-KB queries (e.g. "current listings on vuokraovi") → avg dist ~1.0+
# The 0.95 midpoint gives a safe margin on both sides.
WEB_SEARCH_THRESHOLD = 0.95


def get_context(query: str) -> str:
    """Retrieve top-3 RAG chunks from ChromaDB as a single context string."""
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


def get_context_with_confidence(query: str) -> tuple[str, bool]:
    """
    Retrieve RAG context and determine whether web search is needed.

    Queries ChromaDB for the top-3 most similar chunks. Computes the
    average L2 distance across all three results. If the average exceeds
    WEB_SEARCH_THRESHOLD, the static knowledge base likely does not contain
    a good answer and web search should be used to augment the context.

    Args:
        query: The student's question.

    Returns:
        A tuple (context, needs_web_search) where:
          - context (str):           Top-3 chunks joined by '---'.
          - needs_web_search (bool): True if avg distance > WEB_SEARCH_THRESHOLD.
    """
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
    distances = results["distances"][0]
    context = "\n\n---\n\n".join(chunks)
    avg_distance = sum(distances) / len(distances)
    needs_web_search = avg_distance > WEB_SEARCH_THRESHOLD
    return context, needs_web_search


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What room types are available at Evo campus?"
    print(f"Query: {query}\n")
    context = get_context(query)
    print("Top relevant chunks:\n")
    print(context)
