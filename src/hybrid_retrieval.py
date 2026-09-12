from pathlib import Path
import sys


# ============================================================
# Allow imports from the src directory
# ============================================================

SRC_DIR = Path(__file__).resolve().parent

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))


# ============================================================
# Imports
# ============================================================

from retrieval import retrieve
from bm25_retrieval import retrieve_bm25


# ============================================================
# Retrieval configuration
# ============================================================

DENSE_TOP_K = 20
BM25_TOP_K = 20

FINAL_TOP_K = 5

RRF_K = 60


# ============================================================
# Reciprocal Rank Fusion
# ============================================================

def reciprocal_rank_fusion(
    dense_results: list[dict],
    bm25_results: list[dict],
    top_k: int = FINAL_TOP_K,
) -> list[dict]:
    """
    Combine dense and BM25 retrieval results using
    Reciprocal Rank Fusion (RRF).
    """

    scores = {}
    result_lookup = {}

    # --------------------------------------------------------
    # Dense retrieval contribution
    # --------------------------------------------------------

    for rank, result in enumerate(dense_results, start=1):
        chunk_id = result["chunk_id"]

        scores[chunk_id] = scores.get(chunk_id, 0.0)
        scores[chunk_id] += 1.0 / (RRF_K + rank)

        result_lookup[chunk_id] = result.copy()

    # --------------------------------------------------------
    # BM25 retrieval contribution
    # --------------------------------------------------------

    for rank, result in enumerate(bm25_results, start=1):
        chunk_id = result["chunk_id"]

        scores[chunk_id] = scores.get(chunk_id, 0.0)
        scores[chunk_id] += 1.0 / (RRF_K + rank)

        if chunk_id not in result_lookup:
            result_lookup[chunk_id] = result.copy()

    # --------------------------------------------------------
    # Sort by RRF score
    # --------------------------------------------------------

    ranked_chunk_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    # --------------------------------------------------------
    # Build final results
    # --------------------------------------------------------

    results = []

    for rank, chunk_id in enumerate(
        ranked_chunk_ids[:top_k],
        start=1,
    ):
        result = result_lookup[chunk_id].copy()

        result["rrf_score"] = scores[chunk_id]
        result["rrf_rank"] = rank

        results.append(result)

    return results


# ============================================================
# Hybrid retrieval
# ============================================================

def retrieve_hybrid(
    query: str,
    top_k: int = FINAL_TOP_K,
) -> list[dict]:
    """
    Retrieve financial report chunks using both
    dense embeddings and BM25 lexical retrieval.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    dense_results = retrieve(
        query,
        top_k=DENSE_TOP_K,
    )

    bm25_results = retrieve_bm25(
        query,
        top_k=BM25_TOP_K,
    )

    return reciprocal_rank_fusion(
        dense_results,
        bm25_results,
        top_k=top_k,
    )


# ============================================================
# Manual test
# ============================================================

if __name__ == "__main__":

    query = "What was Microsoft's total revenue in fiscal year 2025?"

    results = retrieve_hybrid(
        query,
        top_k=5,
    )

    print("=" * 80)
    print("HYBRID RETRIEVAL TEST")
    print("=" * 80)

    print(f"\nQuery:\n{query}")

    for result in results:

        print("\n" + "-" * 80)

        print(f"Rank: {result['rrf_rank']}")
        print(f"Chunk ID: {result.get('chunk_id')}")
        print(f"PDF page: {result.get('pdf_page')}")
        print(f"Report page: {result.get('report_page')}")
        print(f"RRF score: {result['rrf_score']:.6f}")

        if "similarity_score" in result:
            print(
                f"Dense similarity: "
                f"{result['similarity_score']:.4f}"
            )

        if "bm25_score" in result:
            print(
                f"BM25 score: "
                f"{result['bm25_score']:.4f}"
            )

        print(f"\n{result['text'][:500]}")

    print("\n" + "=" * 80)
    print("HYBRID RETRIEVAL TEST COMPLETE")
    print("=" * 80)