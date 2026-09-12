def calculate_evidence_score(query: str, chunk: dict) -> float:
    """
    Calculate a query-aware evidence preference score.

    The score does not replace the retrieval score.
    It acts as a small ranking signal that prefers
    appropriate evidence types for the question.

    Returns:
        A float evidence preference score.
    """

    query_lower = query.lower()
    evidence_type = chunk.get("evidence_type", "general")

    score = 0.0

    # ---------------------------------------------------------------
    # Cash-flow questions
    # ---------------------------------------------------------------

    cash_flow_terms = [
        "cash flow",
        "cash flows",
        "cash from operations",
        "operating cash flow",
        "cash from investing",
        "cash from financing",
    ]

    if any(term in query_lower for term in cash_flow_terms):

        if evidence_type == "cash_flow_table":
            score += 0.20

        elif evidence_type == "financial_statement":
            score += 0.08

        elif evidence_type == "narrative":
            score += 0.02

    # ---------------------------------------------------------------
    # Segment questions
    # ---------------------------------------------------------------

    segment_terms = [
        "segment",
        "productivity and business processes",
        "intelligent cloud",
        "more personal computing",
    ]

    if any(term in query_lower for term in segment_terms):

        if evidence_type == "segment_table":
            score += 0.20

        elif evidence_type == "financial_statement":
            score += 0.06

        elif evidence_type == "financial_table":
            score += 0.04

        elif evidence_type == "narrative":
            score += 0.02

    # ---------------------------------------------------------------
    # Product / service revenue questions
    # ---------------------------------------------------------------

    product_terms = [
        "gaming",
        "server products",
        "server products and cloud services",
        "microsoft 365",
        "linkedin",
        "windows",
        "search and news advertising",
        "dynamics",
        "enterprise and partner services",
        "product revenue",
        "service revenue",
        "product and service",
    ]

    if any(term in query_lower for term in product_terms):

        if evidence_type == "revenue_table":
            score += 0.20

            # For "why" questions, narrative evidence is
            # more useful for explaining causes than tables.
            if any(term in query_lower for term in [
                "why",
                "what caused",
                "what drove",
                "what were the reasons",
                "reason for",
            ]):
                score -= 0.10

        elif evidence_type == "financial_statement":
            score += 0.06

        elif evidence_type == "financial_table":
            score += 0.04

        elif evidence_type == "narrative":
            score += 0.02

    # ---------------------------------------------------------------
    # Total revenue questions
    # ---------------------------------------------------------------

    total_revenue_terms = [
        "total revenue",
        "total revenues",
        "revenue for fiscal year",
        "revenue in fiscal year",
        "annual revenue",
    ]

    if any(term in query_lower for term in total_revenue_terms):

        if evidence_type == "financial_statement":
            score += 0.16

        elif evidence_type == "revenue_table":
            score += 0.12

        elif evidence_type == "segment_table":
            score += 0.08

        elif evidence_type == "financial_table":
            score += 0.04

        elif evidence_type == "narrative":
            score += 0.01

    # ---------------------------------------------------------------
    # Asset questions
    # ---------------------------------------------------------------

    asset_terms = [
        "total assets",
        "assets",
        "current assets",
        "non-current assets",
    ]

    if any(term in query_lower for term in asset_terms):

        if evidence_type == "financial_statement":
            score += 0.20

        elif evidence_type == "financial_table":
            score += 0.05

        elif evidence_type == "narrative":
            score += 0.01

    # ---------------------------------------------------------------
    # Liability questions
    # ---------------------------------------------------------------

    liability_terms = [
        "total liabilities",
        "liabilities",
        "current liabilities",
        "non-current liabilities",
    ]

    if any(term in query_lower for term in liability_terms):

        if evidence_type == "financial_statement":
            score += 0.20

        elif evidence_type == "financial_table":
            score += 0.05

        elif evidence_type == "narrative":
            score += 0.01

    # ---------------------------------------------------------------
    # Operating income / net income / EPS
    # ---------------------------------------------------------------

    income_terms = [
        "operating income",
        "net income",
        "net earnings",
        "earnings per share",
        "diluted eps",
        "basic eps",
    ]

    if any(term in query_lower for term in income_terms):

        if evidence_type == "financial_statement":
            score += 0.16

        elif evidence_type == "financial_table":
            score += 0.04

        elif evidence_type == "narrative":
            score += 0.02

    # ---------------------------------------------------------------
    # Comparison questions
    # ---------------------------------------------------------------

    comparison_terms = [
        "compared with",
        "compared to",
        "versus",
        "vs",
        "increase",
        "decrease",
        "growth",
        "grew",
        "declined",
        "change",
    ]

    if any(term in query_lower for term in comparison_terms):

        if evidence_type in {
            "financial_statement",
            "financial_table",
            "segment_table",
            "revenue_table",
        }:
            score += 0.04

        elif evidence_type == "narrative":
            score += 0.05

    # ---------------------------------------------------------------
    # "Why" questions
    # ---------------------------------------------------------------

    why_terms = [
        "why",
        "what caused",
        "what drove",
        "what were the reasons",
        "reason for",
        "driven by",
    ]

    if any(term in query_lower for term in why_terms):

        if evidence_type == "narrative":
            score += 0.15

        elif evidence_type == "financial_table":
            score += 0.03

        elif evidence_type in {
            "financial_statement",
            "segment_table",
            "revenue_table",
        }:
            score += 0.02

    return score


def apply_evidence_scoring(
    query: str,
    candidates: list[dict],
) -> list[dict]:
    """
    Add evidence scores and combined scores to retrieved candidates.

    The original retrieval score is preserved.

    Returns:
        Candidates sorted by combined score.
    """

    scored_candidates = []

    for candidate in candidates:

        result = candidate.copy()

        evidence_score = calculate_evidence_score(
            query,
            result,
        )

        base_score = result.get(
            "financial_score",
            result.get(
                "routing_score",
                result.get(
                    "rrf_score",
                    result.get(
                        "similarity_score",
                        0.0,
                    ),
                ),
            ),
        )

        result["evidence_score"] = evidence_score

        result["combined_score"] = (
            float(base_score) + evidence_score
        )

        scored_candidates.append(result)

    scored_candidates.sort(
        key=lambda item: item["combined_score"],
        reverse=True,
    )

    for rank, candidate in enumerate(
        scored_candidates,
        start=1,
    ):
        candidate["evidence_rank"] = rank

    return scored_candidates


# ===================================================================
# CONTROLLED TEST
# ===================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("EVIDENCE SCORING TEST")
    print("=" * 80)

    test_candidates = [
        {
            "chunk_id": "financial_statement",
            "evidence_type": "financial_statement",
            "financial_score": 0.50,
        },
        {
            "chunk_id": "revenue_table",
            "evidence_type": "revenue_table",
            "financial_score": 0.50,
        },
        {
            "chunk_id": "segment_table",
            "evidence_type": "segment_table",
            "financial_score": 0.50,
        },
        {
            "chunk_id": "narrative",
            "evidence_type": "narrative",
            "financial_score": 0.50,
        },
        {
            "chunk_id": "cash_flow_table",
            "evidence_type": "cash_flow_table",
            "financial_score": 0.50,
        },
    ]

    test_queries = [
        "What was Microsoft's Gaming revenue in FY2025?",
        "What was Microsoft's total revenue in FY2025?",
        "What was Microsoft's net cash from operations in FY2025?",
        "What was Microsoft's highest revenue segment in FY2025?",
        "Why did Gaming revenue increase in FY2025?",
    ]

    for query in test_queries:

        print("\n" + "-" * 80)
        print(f"Query: {query}")
        print("-" * 80)

        results = apply_evidence_scoring(
            query,
            test_candidates,
        )

        for result in results:
            print(
                f"{result['evidence_rank']}. "
                f"{result['chunk_id']:22s} "
                f"evidence={result['evidence_score']:.3f} "
                f"combined={result['combined_score']:.3f}"
            )

    print("\n" + "=" * 80)
    print("EVIDENCE SCORING TEST COMPLETE")
    print("=" * 80)