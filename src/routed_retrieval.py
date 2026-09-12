from hybrid_retrieval import retrieve_hybrid
from query_router import route_query
from query_routing_strategy import get_retrieval_strategy


CANDIDATE_COUNT = 20
FINAL_COUNT = 20

ROUTING_BOOST = 0.002


def calculate_routing_boost(
    text: str,
    preferred_terms: list[str],
) -> float:
    """
    Calculate a small retrieval boost based on the query's
    routed retrieval strategy.

    The boost is intentionally small so that routing helps
    retrieval without completely overriding semantic relevance.
    """

    text_lower = text.lower()

    matched_terms = 0

    for term in preferred_terms:
        if term.lower() in text_lower:
            matched_terms += 1

    if matched_terms == 0:
        return 0.0

    return ROUTING_BOOST * matched_terms


def retrieve_routed(
    query: str,
    top_k: int = FINAL_COUNT,
) -> list[dict]:
    """
    Retrieve documents using:

        Query Router
            ↓
        Retrieval Strategy
            ↓
        Hybrid RRF Retrieval
            ↓
        Small Financial-Aware Routing Boost
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    # ---------------------------------------------------------
    # 1. Determine query type
    # ---------------------------------------------------------

    query_type = route_query(query)

    # ---------------------------------------------------------
    # 2. Get retrieval strategy
    # ---------------------------------------------------------

    strategy = get_retrieval_strategy(query_type)

    preferred_terms = strategy["preferred_terms"]

    # ---------------------------------------------------------
    # 3. Retrieve hybrid candidates
    # ---------------------------------------------------------

    candidates = retrieve_hybrid(
        query=query,
        top_k=CANDIDATE_COUNT,
    )

    # ---------------------------------------------------------
    # 4. Apply routing boost
    # ---------------------------------------------------------

    scored_candidates = []

    for candidate in candidates:

        routing_boost = calculate_routing_boost(
            text=candidate["text"],
            preferred_terms=preferred_terms,
        )

        result = candidate.copy()

        result["query_type"] = query_type

        result["routing_boost"] = routing_boost

        result["routing_score"] = (
            result["rrf_score"]
            + routing_boost
        )

        scored_candidates.append(result)

    # ---------------------------------------------------------
    # 5. Sort by routing-aware score
    # ---------------------------------------------------------

    scored_candidates.sort(
        key=lambda item: item["routing_score"],
        reverse=True,
    )

    # ---------------------------------------------------------
    # 6. Assign final ranks
    # ---------------------------------------------------------

    results = []

    for rank, candidate in enumerate(
        scored_candidates[:top_k],
        start=1,
    ):

        candidate["routing_rank"] = rank

        results.append(candidate)

    return results


def main():
    """
    Test routing-aware retrieval.
    """

    test_questions = [
        "What were Microsoft's total assets as of June 30, 2025?",
        "What was Microsoft's net cash from operations in fiscal year 2025?",
        "What was Microsoft's Gaming revenue in fiscal year 2025?",
        "What were Microsoft's total revenues in fiscal years 2025, 2024, and 2023?",
        "Which Microsoft segment had the highest revenue in fiscal year 2025?",
    ]

    print("=" * 80)
    print("ROUTING-AWARE HYBRID RETRIEVAL")
    print("=" * 80)

    for question_number, question in enumerate(
        test_questions,
        start=1,
    ):

        print("\n" + "=" * 80)
        print(f"QUESTION {question_number}")
        print("=" * 80)

        print(f"\nQuestion: {question}")

        query_type = route_query(question)

        strategy = get_retrieval_strategy(
            query_type
        )

        print(
            f"\nQuery type: {query_type}"
        )

        print(
            f"Strategy: {strategy['description']}"
        )

        results = retrieve_routed(
            query=question,
            top_k=5,
        )

        print("\nTop 5 routing-aware results:")

        for result in results:

            print(
                f"\nRank {result['routing_rank']} | "
                f"Routing score: "
                f"{result['routing_score']:.6f}"
            )

            print(
                f"RRF score: "
                f"{result['rrf_score']:.6f}"
            )

            print(
                f"Routing boost: "
                f"{result['routing_boost']:.6f}"
            )

            print(
                f"Page: "
                f"{result['report_page']}"
            )

            print(
                f"Chunk: "
                f"{result['chunk_id']}"
            )

    print("\n" + "=" * 80)
    print("ROUTING-AWARE RETRIEVAL TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()