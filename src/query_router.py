import re


def route_query(query: str) -> str:
    """
    Classify a financial-report question into a retrieval category.

    Returns one of:
        - financial_statement
        - cash_flow
        - table_lookup
        - comparison
        - multi_year_table
        - segment_comparison
        - direct_fact
        - general
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    query_lower = query.lower()

    # ---------------------------------------------------------
    # 1. Cash flow questions
    # ---------------------------------------------------------

    cash_flow_terms = [
        "cash flow",
        "cash from operations",
        "net cash from operations",
        "operating cash flow",
        "cash used in financing",
        "cash used in investing",
        "financing activities",
        "investing activities",
    ]

    if any(term in query_lower for term in cash_flow_terms):
        return "cash_flow"

    # ---------------------------------------------------------
    # 2. Comparison questions
    # ---------------------------------------------------------

    comparison_terms = [
        "compared with",
        "compared to",
        "comparison",
        "increase",
        "decrease",
        "growth",
        "grew",
        "declined",
        "change from",
        "change between",
        "difference between",
        "versus",
        "vs.",
    ]

    if any(term in query_lower for term in comparison_terms):
        return "comparison"

    # ---------------------------------------------------------
    # 3. Multi-year table questions
    # ---------------------------------------------------------

    years = re.findall(
        r"\b20(?:2[0-9]|3[0-9])\b",
        query_lower,
    )

    multi_year_terms = [
        "years",
        "fiscal years",
        "year over year",
        "2025, 2024",
        "2024, 2023",
        "2025 and 2024",
        "2024 and 2023",
    ]

    if len(set(years)) >= 2:
        return "multi_year_table"

    if any(term in query_lower for term in multi_year_terms):
        return "multi_year_table"

    # ---------------------------------------------------------
    # 4. Segment comparison
    # ---------------------------------------------------------

    segment_terms = [
        "segment",
        "segments",
        "which segment",
        "highest segment",
        "lowest segment",
        "segment revenue",
        "segment profit",
    ]

    if any(term in query_lower for term in segment_terms):
        return "segment_comparison"

    # ---------------------------------------------------------
    # 5. Table lookup questions
    # ---------------------------------------------------------

    table_terms = [
        "how much revenue",
        "how much did",
        "total revenue from",
        "revenue from",
        "revenues from",
        "product revenue",
        "service revenue",
        "gaming revenue",
        "server products",
        "cloud services",
        "microsoft cloud",
        "linkedin revenue",
        "windows revenue",
        "search and news advertising",
    ]

    if any(term in query_lower for term in table_terms):
        return "table_lookup"

    # ---------------------------------------------------------
    # 6. Financial statement questions
    # ---------------------------------------------------------

    statement_terms = [
        "total assets",
        "current assets",
        "current liabilities",
        "total liabilities",
        "stockholders' equity",
        "shareholders' equity",
        "balance sheet",
        "accounts receivable",
        "inventories",
        "goodwill",
        "intangible assets",
        "long-term debt",
        "cash and cash equivalents",
    ]

    if any(term in query_lower for term in statement_terms):
        return "financial_statement"

    # ---------------------------------------------------------
    # 7. Direct financial facts
    # ---------------------------------------------------------

    direct_fact_terms = [
        "what was",
        "what were",
        "how much was",
        "how much were",
        "what is",
        "what are",
        "how many",
    ]

    if any(term in query_lower for term in direct_fact_terms):
        return "direct_fact"

    # ---------------------------------------------------------
    # 8. General fallback
    # ---------------------------------------------------------

    return "general"


def main():
    """
    Test the query router interactively.
    """

    print("=" * 70)
    print("FINANCIAL QUERY ROUTER")
    print("=" * 70)

    print("\nEnter a question.")
    print("Type 'exit' to stop.\n")

    while True:

        query = input("Question: ").strip()

        if query.lower() == "exit":
            print("\nExiting query router.")
            break

        if not query:
            print("Please enter a question.\n")
            continue

        category = route_query(query)

        print(
            f"\nQuery type: {category}\n"
        )


if __name__ == "__main__":
    main()