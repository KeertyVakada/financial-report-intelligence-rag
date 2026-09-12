from typing import Literal


QueryType = Literal[
    "financial_statement",
    "cash_flow",
    "table_lookup",
    "comparison",
    "multi_year_table",
    "segment_comparison",
    "direct_fact",
    "general",
]


RETRIEVAL_STRATEGIES = {
    "financial_statement": {
        "description": "Prioritize balance-sheet and financial-statement evidence.",
        "preferred_terms": [
            "balance sheet",
            "assets",
            "liabilities",
            "equity",
            "cash",
            "debt",
            "receivables",
            "inventories",
            "goodwill",
        ],
    },
    "cash_flow": {
        "description": "Prioritize cash-flow statement evidence.",
        "preferred_terms": [
            "cash flow",
            "cash from operations",
            "operating activities",
            "investing activities",
            "financing activities",
        ],
    },
    "table_lookup": {
        "description": "Prioritize structured product, service, and revenue tables.",
        "preferred_terms": [
            "revenue",
            "revenues",
            "products",
            "services",
            "gaming",
            "server",
            "cloud",
            "linkedin",
            "windows",
        ],
    },
    "comparison": {
        "description": "Prioritize evidence needed to compare financial values across periods.",
        "preferred_terms": [
            "increase",
            "decrease",
            "growth",
            "decline",
            "change",
            "difference",
            "2025",
            "2024",
            "2023",
        ],
    },
    "multi_year_table": {
        "description": "Prioritize tables containing multiple fiscal years.",
        "preferred_terms": [
            "2025",
            "2024",
            "2023",
            "fiscal years",
            "years",
        ],
    },
    "segment_comparison": {
        "description": "Prioritize segment-level financial information.",
        "preferred_terms": [
            "segment",
            "segments",
            "revenue",
            "operating income",
            "profit",
        ],
    },
    "direct_fact": {
        "description": "Use general financial-report retrieval for direct factual questions.",
        "preferred_terms": [
            "revenue",
            "income",
            "expense",
            "earnings",
            "profit",
            "assets",
            "liabilities",
        ],
    },
    "general": {
        "description": "Use general retrieval without additional financial specialization.",
        "preferred_terms": [],
    },
}


def get_retrieval_strategy(
    query_type: QueryType,
) -> dict:
    """
    Return the retrieval strategy associated with a query type.
    """

    if query_type not in RETRIEVAL_STRATEGIES:
        raise ValueError(
            f"Unknown query type: {query_type}"
        )

    return RETRIEVAL_STRATEGIES[query_type].copy()


def main():
    """
    Test retrieval strategies for each query type.
    """

    print("=" * 80)
    print("QUERY ROUTING RETRIEVAL STRATEGIES")
    print("=" * 80)

    for query_type, strategy in RETRIEVAL_STRATEGIES.items():

        print("\n" + "-" * 80)
        print(f"Query type: {query_type}")

        print(
            f"\nDescription:\n"
            f"{strategy['description']}"
        )

        print(
            "\nPreferred terms:"
        )

        if strategy["preferred_terms"]:
            for term in strategy["preferred_terms"]:
                print(f"  - {term}")
        else:
            print("  - None")

    print("\n" + "=" * 80)
    print("STRATEGY TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()