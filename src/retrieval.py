from pathlib import Path
import json

import numpy as np
from sentence_transformers import SentenceTransformer


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.json"
EMBEDDINGS_PATH = PROJECT_ROOT / "data" / "processed" / "embeddings.npy"


# ============================================================
# Validate required files
# ============================================================

if not CHUNKS_PATH.exists():
    raise FileNotFoundError(
        f"Chunks file not found:\n{CHUNKS_PATH}\n\n"
        "Run save_chunks.py first to create chunks.json."
    )

if not EMBEDDINGS_PATH.exists():
    raise FileNotFoundError(
        f"Embeddings file not found:\n{EMBEDDINGS_PATH}\n\n"
        "Run embeddings.py first to create embeddings.npy."
    )


# ============================================================
# Load chunks
# ============================================================

with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
    chunks = json.load(file)


# ============================================================
# Load embeddings
# ============================================================

embeddings = np.load(EMBEDDINGS_PATH)


# ============================================================
# Validate alignment
# ============================================================

if len(chunks) != len(embeddings):
    raise ValueError(
        "Mismatch between chunks and embeddings.\n"
        f"Chunks: {len(chunks)}\n"
        f"Embeddings: {len(embeddings)}"
    )


# ============================================================
# Load embedding model
# ============================================================

MODEL_NAME = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(MODEL_NAME)


# ============================================================
# Dense retrieval
# ============================================================

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Retrieve the most relevant chunks using dense embeddings.

    Args:
        query: User's question.
        top_k: Number of chunks to return.

    Returns:
        Ranked list of retrieved chunks.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    # Encode query
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")

    # Cosine similarity because embeddings are normalized
    similarities = embeddings @ query_embedding

    # Get top results
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []

    for rank, index in enumerate(top_indices, start=1):
        chunk = chunks[int(index)].copy()

        chunk["similarity_score"] = float(similarities[index])
        chunk["dense_rank"] = rank

        results.append(chunk)

    return results


# ============================================================
# Simple manual test
# ============================================================

if __name__ == "__main__":
    query = "What was Microsoft's total revenue in fiscal year 2025?"

    results = retrieve(query, top_k=5)

    print("=" * 80)
    print("DENSE RETRIEVAL TEST")
    print("=" * 80)

    print(f"\nQuery:\n{query}")

    for result in results:
        print("\n" + "-" * 80)
        print(f"Rank: {result['dense_rank']}")
        print(f"Chunk ID: {result.get('chunk_id')}")
        print(f"PDF page: {result.get('pdf_page')}")
        print(f"Report page: {result.get('report_page')}")
        print(f"Similarity: {result['similarity_score']:.4f}")
        print(f"\n{result['text'][:500]}")

    print("\n" + "=" * 80)