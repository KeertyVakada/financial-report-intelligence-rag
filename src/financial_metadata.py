import re


def detect_financial_section(text: str) -> str:
    """
    Detect the likely financial section represented by a chunk.
    """

    text_lower = text.lower()

    if any(
        term in text_lower
        for term in [
            "consolidated statements of cash flows",
            "net cash from operations",
            "cash flows from operations",
            "cash flows from investing",
            "cash flows from financing",
        ]
    ):
        return "cash_flow"

    if any(
        term in text_lower
        for term in [
            "consolidated balance sheets",
            "total assets",
            "total liabilities",
            "stockholders' equity",
            "shareholders' equity",
        ]
    ):
        return "balance_sheet"

    if any(
        term in text_lower
        for term in [
            "consolidated statements of income",
            "income before income taxes",
            "net income",
            "operating income",
        ]
    ):
        return "income_statement"

    if any(
        term in text_lower
        for term in [
            "revenue by product and service",
            "revenue by product",
            "revenue by service",
            "revenue was",
            "revenues were",
        ]
    ):
        return "revenue"

    if any(
        term in text_lower
        for term in [
            "intelligent cloud",
            "more personal computing",
            "productivity and business processes",
        ]
    ):
        return "segment"

    return "general"


def detect_table(text: str) -> bool:
    """
    Detect whether a chunk likely contains tabular financial data.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) < 3:
        return False

    numeric_lines = 0

    for line in lines:
        numbers = re.findall(
            r"\$?\(?\d[\d,]*(?:\.\d+)?\)?",
            line,
        )

        if len(numbers) >= 2:
            numeric_lines += 1

    return numeric_lines >= 2


def detect_years(text: str) -> list[int]:
    """
    Extract fiscal/calendar years from a chunk.
    """

    years = re.findall(
        r"\b20(?:2[0-9]|3[0-9])\b",
        text,
    )

    return sorted(set(int(year) for year in years))


def create_financial_metadata(chunk: dict) -> dict:
    """
    Create lightweight financial metadata for one chunk.
    """

    text = chunk["text"]
    text_lower = text.lower()

    years = detect_years(text)

    metadata = {
        "financial_section": detect_financial_section(text),
        "contains_table": detect_table(text),
        "contains_years": len(years) > 0,
        "years": years,
        "contains_total": "total" in text_lower,
        "contains_revenue": "revenue" in text_lower
        or "revenues" in text_lower,
        "contains_assets": "assets" in text_lower,
        "contains_liabilities": "liabilities" in text_lower,
        "contains_cash_flow": (
            "cash flow" in text_lower
            or "cash flows" in text_lower
            or "net cash from operations" in text_lower
        ),
        "contains_segment": (
            "segment" in text_lower
            or "intelligent cloud" in text_lower
            or "more personal computing" in text_lower
            or "productivity and business processes"
            in text_lower
        ),
        "contains_microsoft_cloud": (
            "microsoft cloud" in text_lower
        ),
        "contains_gaming": "gaming" in text_lower,
        "contains_server": (
            "server products" in text_lower
            or "server and cloud services" in text_lower
        ),
    }

    return metadata


def add_financial_metadata(chunks: list[dict]) -> list[dict]:
    """
    Add financial metadata to every chunk.
    """

    enriched_chunks = []

    for chunk in chunks:
        enriched_chunk = chunk.copy()

        metadata = create_financial_metadata(chunk)

        enriched_chunk.update(metadata)

        enriched_chunks.append(enriched_chunk)

    return enriched_chunks


def main():
    print("=" * 80)
    print("FINANCIAL METADATA TEST")
    print("=" * 80)

    test_chunks = [
        {
            "chunk_id": "test_revenue",
            "text": """
            Revenue was $281,724 million in fiscal year 2025
            compared with $245,122 million in fiscal year 2024.
            Total revenue increased 15%.
            """,
        },
        {
            "chunk_id": "test_cloud",
            "text": """
            Microsoft Cloud revenue was $168.9 billion in
            fiscal year 2025, compared with $137.7 billion
            in fiscal year 2024.
            """,
        },
        {
            "chunk_id": "test_assets",
            "text": """
            Total assets were $619,003 million as of
            June 30, 2025.
            """,
        },
        {
            "chunk_id": "test_cash_flow",
            "text": """
            Net cash from operations was $136,162 million
            in fiscal year 2025.
            """,
        },
    ]

    enriched_chunks = add_financial_metadata(test_chunks)

    for chunk in enriched_chunks:
        print("\n" + "-" * 80)
        print(f"Chunk: {chunk['chunk_id']}")

        print("\nFinancial section:")
        print(f"  {chunk['financial_section']}")

        print("\nContains table:")
        print(f"  {chunk['contains_table']}")

        print("\nYears:")
        print(f"  {chunk['years']}")

        print("\nContains total:")
        print(f"  {chunk['contains_total']}")

        print("\nContains revenue:")
        print(f"  {chunk['contains_revenue']}")

        print("\nContains assets:")
        print(f"  {chunk['contains_assets']}")

        print("\nContains cash flow:")
        print(f"  {chunk['contains_cash_flow']}")

        print("\nContains segment:")
        print(f"  {chunk['contains_segment']}")

        print("\nContains Microsoft Cloud:")
        print(f"  {chunk['contains_microsoft_cloud']}")

        print("\nContains Gaming:")
        print(f"  {chunk['contains_gaming']}")

        print("\nContains Server:")
        print(f"  {chunk['contains_server']}")

    print("\n" + "=" * 80)
    print("FINANCIAL METADATA TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()