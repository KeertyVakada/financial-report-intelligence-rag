def detect_evidence_type(chunk: dict) -> str:
    text = chunk["text"].lower()

    # 1. Cash-flow table
    if any(term in text for term in [
        "consolidated statements of cash flows",
        "net cash from operations",
        "cash flows from operations",
        "cash flows from investing",
        "cash flows from financing",
    ]):
        return "cash_flow_table"

    # 2. Segment table
    if (
        "segment revenue" in text
        and "operating income" in text
        and "year ended june 30" in text
    ):
        return "segment_table"

    if (
        "productivity and business processes" in text
        and "intelligent cloud" in text
        and "more personal computing" in text
        and "revenue" in text
        and "year ended june 30" in text
    ):
        return "segment_table"

    # 3. Product/service revenue table
    if (
        "revenue, classified by significant product"
        in text
        and "gaming" in text
        and "server products" in text
    ):
        return "revenue_table"

    # 4. Financial statements
    if any(term in text for term in [
        "balance sheets",
        "total assets",
        "total liabilities",
        "stockholders’ equity",
        "stockholders' equity",
        "income statements",
        "total revenue",
        "operating income",
        "net income",
    ]):
        if any(term in text for term in [
            "financial statements",
            "balance sheets",
            "income statements",
            "assets",
            "liabilities",
        ]):
            return "financial_statement"

    # 5. Other financial tables
    if (
        chunk.get("contains_table", False)
        and chunk.get("contains_revenue", False)
    ):
        return "financial_table"

    # 6. Narrative
    narrative_terms = [
        "revenue increased",
        "revenue decreased",
        "revenue grew",
        "revenue declined",
        "driven by",
        "primarily due to",
        "we expect",
        "we believe",
    ]

    if any(term in text for term in narrative_terms):
        return "narrative"

    return "general"


def add_evidence_types(chunks):
    processed_chunks = []

    for chunk in chunks:
        updated_chunk = chunk.copy()
        updated_chunk["evidence_type"] = detect_evidence_type(updated_chunk)
        processed_chunks.append(updated_chunk)

    return processed_chunks


def main():
    print("=" * 80)
    print("EVIDENCE TYPE TEST")
    print("=" * 80)

    test_chunks = [
        {
            "chunk_id": "income_statement",
            "text": """
            FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA

            INCOME STATEMENTS

            (In millions)

            Year Ended June 30,
            2025 2024 2023

            Revenue:
            Product
            $63,946 $64,773 $64,699

            Total revenue
            281,724 245,122 211,915

            Operating income
            128,528 109,433 88,523
            """,
            "contains_table": True,
            "contains_revenue": True,
        },
        {
            "chunk_id": "cash_flow",
            "text": """
            CONSOLIDATED STATEMENTS OF CASH FLOWS

            Net cash from operations
            136,162 118,548 87,582

            Cash flows from investing
            """,
            "contains_table": True,
            "contains_revenue": False,
        },
        {
            "chunk_id": "segment_table",
            "text": """
            Segment revenue, cost of revenue, operating expenses,
            and operating income were as follows during the periods
            presented.

            (In millions)

            Year Ended June 30,
            2025 2024 2023

            Productivity and Business Processes
            Revenue
            $120,810 $106,820 $94,151

            Intelligent Cloud
            Revenue
            $106,265 $87,464 $72,944

            More Personal Computing
            Revenue
            $54,649 $50,838 $44,820

            Operating Income
            """,
            "contains_table": True,
            "contains_revenue": True,
        },
        {
            "chunk_id": "revenue_table",
            "text": """
            Revenue, classified by significant product and service
            offerings, was as follows:

            (In millions)

            Year Ended June 30,
            2025 2024 2023

            Server products and cloud services
            $98,435 $79,828 $65,007

            Gaming
            23,455 21,503 15,466

            LinkedIn
            17,812 16,372 14,989

            Total
            $281,724 $245,122 $211,915
            """,
            "contains_table": True,
            "contains_revenue": True,
        },
        {
            "chunk_id": "narrative",
            "text": """
            Gaming revenue increased $2.0 billion or 9% driven by
            growth in Xbox content and services, offset in part by
            a decline in Xbox hardware.
            """,
            "contains_table": False,
            "contains_revenue": True,
        },
    ]

    enriched_chunks = add_evidence_types(
        test_chunks
    )

    for chunk in enriched_chunks:
        print("\n" + "-" * 80)
        print(
            f"Chunk: {chunk['chunk_id']}"
        )
        print(
            f"Evidence type: "
            f"{chunk['evidence_type']}"
        )

    print("\n" + "=" * 80)
    print("EVIDENCE TYPE TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()