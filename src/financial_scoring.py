import re


def detect_query_signals(query: str) -> dict:
    """
    Detect financial intent signals from a user query.

    These signals are used to compare the query's intent with
    metadata attached to retrieved document chunks.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    query_lower = query.lower()

    years = sorted(
        set(
            int(year)
            for year in re.findall(
                r"\b20(?:2[0-9]|3[0-9])\b",
                query_lower,
            )
        )
    )

    signals = {
        "asks_total": any(
            phrase in query_lower
            for phrase in [
                "total revenue",
                "total revenues",
                "total assets",
                "total liabilities",
                "total income",
                "total cost",
                "overall revenue",
                "overall revenues",
            ]
        ),
        "asks_revenue": (
            "revenue" in query_lower
            or "revenues" in query_lower
        ),
        "asks_assets": "assets" in query_lower,
        "asks_liabilities": "liabilities" in query_lower,
        "asks_cash_flow": any(
            phrase in query_lower
            for phrase in [
                "cash flow",
                "cash from operations",
                "net cash from operations",
                "operating cash flow",
                "cash used in investing",
                "cash used in financing",
            ]
        ),
        "asks_segment": any(
            phrase in query_lower
            for phrase in [
                "segment",
                "segments",
            ]
        ),
        "asks_product_or_service": any(
            phrase in query_lower
            for phrase in [
                "product",
                "products",
                "service",
                "services",
                "gaming",
                "server products",
                "cloud services",
                "linkedin",
                "windows",
            ]
        ),
        "asks_microsoft_cloud": (
            "microsoft cloud" in query_lower
        ),
        "asks_gaming": "gaming" in query_lower,
        "asks_server": (
            "server" in query_lower
            or "server products" in query_lower
        ),
        "asks_comparison": any(
            phrase in query_lower
            for phrase in [
                "compared",
                "comparison",
                "increase",
                "decrease",
                "growth",
                "grew",
                "declined",
                "change",
                "difference",
                "versus",
                "vs.",
            ]
        ),
        "asks_multi_year": (
            len(years) >= 2
            or any(
                phrase in query_lower
                for phrase in [
                    "fiscal years",
                    "multiple years",
                    "over the years",
                    "year over year",
                ]
            )
        ),
        "years": years,
    }

    return signals


def calculate_financial_score(
    query: str,
    chunk: dict,
) -> float:
    """
    Calculate an interpretable financial relevance score.

    The score is intentionally small relative to the original
    retrieval score. It acts as a ranking adjustment rather
    than replacing dense/BM25 retrieval.
    """

    signals = detect_query_signals(query)

    score = 0.0

    # --------------------------------------------------------------
    # 1. Total-company intent
    # --------------------------------------------------------------

    if signals["asks_total"]:
        if chunk.get("contains_total", False):
            score += 0.08

        # A query asking for total company revenue should prefer
        # company-wide financial statements/tables.
        if signals["asks_revenue"]:
            if chunk.get("financial_section") in [
                "income_statement",
                "revenue",
            ]:
                score += 0.06

            # Microsoft Cloud is a component of Microsoft's
            # overall revenue, not total company revenue.
            if chunk.get("contains_microsoft_cloud", False):
                score -= 0.10

    # --------------------------------------------------------------
    # 2. Revenue intent
    # --------------------------------------------------------------

    if signals["asks_revenue"]:
        if chunk.get("contains_revenue", False):
            score += 0.04

    # --------------------------------------------------------------
    # 3. Assets intent
    # --------------------------------------------------------------

    if signals["asks_assets"]:
        if chunk.get("contains_assets", False):
            score += 0.10

        if chunk.get("financial_section") == "balance_sheet":
            score += 0.08

    # --------------------------------------------------------------
    # 4. Liabilities intent
    # --------------------------------------------------------------

    if signals["asks_liabilities"]:
        if chunk.get("contains_liabilities", False):
            score += 0.10

        if chunk.get("financial_section") == "balance_sheet":
            score += 0.08

    # --------------------------------------------------------------
    # 5. Cash-flow intent
    # --------------------------------------------------------------

    if signals["asks_cash_flow"]:
        if chunk.get("contains_cash_flow", False):
            score += 0.12

        if chunk.get("financial_section") == "cash_flow":
            score += 0.10

    # --------------------------------------------------------------
    # 6. Segment intent
    # --------------------------------------------------------------

    if signals["asks_segment"]:
        if chunk.get("contains_segment", False):
            score += 0.08

        if chunk.get("financial_section") == "segment":
            score += 0.08

    # --------------------------------------------------------------
    # 7. Product/service intent
    # --------------------------------------------------------------

    if signals["asks_product_or_service"]:
        if chunk.get("contains_revenue", False):
            score += 0.03

    # --------------------------------------------------------------
    # 8. Microsoft Cloud intent
    # --------------------------------------------------------------

    if signals["asks_microsoft_cloud"]:
        if chunk.get("contains_microsoft_cloud", False):
            score += 0.15

    # --------------------------------------------------------------
    # 9. Gaming intent
    # --------------------------------------------------------------

    if signals["asks_gaming"]:
        if chunk.get("contains_gaming", False):
            score += 0.15

    # --------------------------------------------------------------
    # 10. Server intent
    # --------------------------------------------------------------

    if signals["asks_server"]:
        if chunk.get("contains_server", False):
            score += 0.15

    # --------------------------------------------------------------
    # 11. Multi-year intent
    # --------------------------------------------------------------

    if signals["asks_multi_year"]:
        chunk_years = set(chunk.get("years", []))

        requested_years = set(signals["years"])

        if requested_years:
            overlap = len(
                chunk_years.intersection(requested_years)
            )

            score += 0.02 * overlap

        if len(chunk_years) >= 2:
            score += 0.03

    return score


def apply_financial_scoring(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """
    Apply financial-aware scoring to retrieved candidates.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if not candidates:
        return []

    scored_candidates = []

    for candidate in candidates:
        financial_score = calculate_financial_score(
            query=query,
            chunk=candidate,
        )

        result = candidate.copy()

        result["financial_score"] = financial_score

        base_score = result.get(
            "rrf_score",
            result.get("routing_score", 0.0),
        )

        result["final_financial_score"] = (
            base_score + financial_score
        )

        scored_candidates.append(result)

    scored_candidates.sort(
        key=lambda item: item["final_financial_score"],
        reverse=True,
    )

    results = []

    for rank, candidate in enumerate(
        scored_candidates[:top_k],
        start=1,
    ):
        candidate["financial_rank"] = rank
        results.append(candidate)

    return results


def main():
    print("=" * 80)
    print("FINANCIAL SCORING TEST")
    print("=" * 80)

    test_chunks = [
        {
            "chunk_id": "total_revenue",
            "financial_section": "income_statement",
            "contains_total": True,
            "contains_revenue": True,
            "contains_microsoft_cloud": False,
            "contains_assets": False,
            "contains_liabilities": False,
            "contains_cash_flow": False,
            "contains_segment": False,
            "contains_gaming": False,
            "contains_server": False,
            "years": [2023, 2024, 2025],
            "rrf_score": 0.0160,
        },
        {
            "chunk_id": "microsoft_cloud",
            "financial_section": "revenue",
            "contains_total": True,
            "contains_revenue": True,
            "contains_microsoft_cloud": True,
            "contains_assets": False,
            "contains_liabilities": False,
            "contains_cash_flow": False,
            "contains_segment": False,
            "contains_gaming": False,
            "contains_server": False,
            "years": [2023, 2024, 2025],
            "rrf_score": 0.0200,
        },
        {
            "chunk_id": "gaming",
            "financial_section": "revenue",
            "contains_total": True,
            "contains_revenue": True,
            "contains_microsoft_cloud": False,
            "contains_assets": False,
            "contains_liabilities": False,
            "contains_cash_flow": False,
            "contains_segment": False,
            "contains_gaming": True,
            "contains_server": False,
            "years": [2023, 2024, 2025],
            "rrf_score": 0.0150,
        },
    ]

    test_queries = [
        "What were Microsoft's total revenues in fiscal years 2025, 2024, and 2023?",
        "What was Microsoft's Microsoft Cloud revenue in fiscal year 2025?",
        "What was Microsoft's Gaming revenue in fiscal year 2025?",
    ]

    for query in test_queries:
        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        signals = detect_query_signals(query)

        print("\nDetected signals:")

        for key, value in signals.items():
            print(f"  {key}: {value}")

        results = apply_financial_scoring(
            query=query,
            candidates=test_chunks,
            top_k=3,
        )

        print("\nRanked candidates:")

        for result in results:
            print(
                f"\nRank {result['financial_rank']}"
            )
            print(
                f"Chunk: {result['chunk_id']}"
            )
            print(
                f"Base score: "
                f"{result['rrf_score']:.6f}"
            )
            print(
                f"Financial score: "
                f"{result['financial_score']:.6f}"
            )
            print(
                f"Final score: "
                f"{result['final_financial_score']:.6f}"
            )

    print("\n" + "=" * 80)
    print("FINANCIAL SCORING TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()