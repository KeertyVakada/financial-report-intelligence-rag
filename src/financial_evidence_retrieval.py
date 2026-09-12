from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from hybrid_retrieval import retrieve_hybrid
from financial_metadata import add_financial_metadata
from financial_scoring import apply_financial_scoring
from evidence_type import add_evidence_types
from evidence_scoring import apply_evidence_scoring


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

CANDIDATE_COUNT = 20
FINAL_COUNT = 5


# -------------------------------------------------------------------
# Financial + Evidence-aware retrieval
# -------------------------------------------------------------------

def retrieve_financial_evidence(
    query: str,
    top_k: int = FINAL_COUNT,
) -> list[dict]:
    """
    Retrieve document chunks using:

    1. Hybrid retrieval
    2. Financial metadata
    3. Financial scoring
    4. Evidence type detection
    5. Evidence-aware scoring

    Returns:
        Ranked list of final candidates.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    # ---------------------------------------------------------------
    # Step 1: Hybrid retrieval
    # ---------------------------------------------------------------

    candidates = retrieve_hybrid(
        query,
        top_k=CANDIDATE_COUNT,
    )

    if not candidates:
        return []

    # ---------------------------------------------------------------
    # Step 2: Add financial metadata
    # ---------------------------------------------------------------

    candidates = add_financial_metadata(candidates)

    # ---------------------------------------------------------------
    # Step 3: Apply financial scoring
    # ---------------------------------------------------------------

    candidates = apply_financial_scoring(
        query,
        candidates,
        top_k=CANDIDATE_COUNT
    )

    # ---------------------------------------------------------------
    # Step 4: Detect evidence types
    # ---------------------------------------------------------------

    candidates = add_evidence_types(candidates)

    # ---------------------------------------------------------------
    # Step 5: Apply evidence scoring
    # ---------------------------------------------------------------

    candidates = apply_evidence_scoring(
        query,
        candidates,
    )

    # ---------------------------------------------------------------
    # Step 6: Keep final top-k
    # ---------------------------------------------------------------

    results = candidates[:top_k]

    # ---------------------------------------------------------------
    # Step 7: Add final rank
    # ---------------------------------------------------------------

    for rank, result in enumerate(
        results,
        start=1,
    ):
        result["final_rank"] = rank

    return results


# ===================================================================
# INTERACTIVE TEST
# ===================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("FINANCIAL + EVIDENCE RETRIEVAL TEST")
    print("=" * 80)

    test_queries = [
        "What was Microsoft's total revenue in FY2025?",
        "What was Microsoft's Gaming revenue in FY2025?",
        "What was Microsoft's net cash from operations in FY2025?",
        "What was Microsoft's highest revenue segment in FY2025?",
        "Why did Gaming revenue increase in FY2025?",
        "What were Microsoft's total revenues in 2025, 2024, and 2023?",
    ]

    for query in test_queries:

        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        results = retrieve_financial_evidence(query)

        for result in results:

            print("\n" + "-" * 80)

            print(
                f"Rank: {result['final_rank']}"
            )

            print(
                f"Chunk: {result['chunk_id']}"
            )

            print(
                f"PDF page: {result['pdf_page']}"
            )

            print(
                f"Report page: {result['report_page']}"
            )

            print(
                f"Evidence type: "
                f"{result.get('evidence_type')}"
            )

            print(
                f"RRF score: "
                f"{result.get('rrf_score', 0.0):.6f}"
            )

            print(
                f"Financial score: "
                f"{result.get('financial_score', 0.0):.6f}"
            )

            print(
                f"Evidence score: "
                f"{result.get('evidence_score', 0.0):.6f}"
            )

            print(
                f"Combined score: "
                f"{result.get('combined_score', 0.0):.6f}"
            )

            print("\nText preview:")
            print(
                result["text"][:600]
            )

    print("\n" + "=" * 80)
    print("FINANCIAL + EVIDENCE RETRIEVAL TEST COMPLETE")
    print("=" * 80)