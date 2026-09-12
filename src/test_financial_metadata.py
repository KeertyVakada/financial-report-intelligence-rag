import json

from financial_metadata import add_financial_metadata


CHUNKS_PATH = "../data/processed/chunks.json"


def load_chunks(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def print_matching_chunks(
    chunks: list[dict],
    label: str,
    condition,
) -> None:
    print("\n" + "=" * 80)
    print(label)
    print("=" * 80)

    matches = [
        chunk
        for chunk in chunks
        if condition(chunk)
    ]

    print(f"\nMatching chunks: {len(matches)}")

    for chunk in matches:
        print("\n" + "-" * 80)
        print(f"Chunk: {chunk['chunk_id']}")
        print(f"PDF page: {chunk['pdf_page']}")
        print(f"Report page: {chunk['report_page']}")
        print(f"Financial section: {chunk['financial_section']}")
        print(f"Contains table: {chunk['contains_table']}")
        print(f"Years: {chunk['years']}")
        print(f"Contains total: {chunk['contains_total']}")
        print(f"Contains revenue: {chunk['contains_revenue']}")
        print(
            f"Contains Microsoft Cloud: "
            f"{chunk['contains_microsoft_cloud']}"
        )

        print("\nText preview:")
        print(chunk["text"][:1000])


def main():
    print("=" * 80)
    print("REAL MICROSOFT REPORT FINANCIAL METADATA TEST")
    print("=" * 80)

    chunks = load_chunks(CHUNKS_PATH)

    print(f"\nLoaded chunks: {len(chunks)}")

    enriched_chunks = add_financial_metadata(chunks)

    print(f"Enriched chunks: {len(enriched_chunks)}")

    # ------------------------------------------------------------------
    # TEST 1: Total assets
    # ------------------------------------------------------------------

    print_matching_chunks(
        enriched_chunks,
        "TEST 1: TOTAL ASSETS",
        lambda chunk: (
            "total assets" in chunk["text"].lower()
        ),
    )

    # ------------------------------------------------------------------
    # TEST 2: Net cash from operations
    # ------------------------------------------------------------------

    print_matching_chunks(
        enriched_chunks,
        "TEST 2: NET CASH FROM OPERATIONS",
        lambda chunk: (
            "net cash from operations"
            in chunk["text"].lower()
        ),
    )

    # ------------------------------------------------------------------
    # TEST 3: Gaming revenue
    # ------------------------------------------------------------------

    print_matching_chunks(
        enriched_chunks,
        "TEST 3: GAMING REVENUE",
        lambda chunk: (
            "gaming" in chunk["text"].lower()
            and "revenue" in chunk["text"].lower()
        ),
    )

    # ------------------------------------------------------------------
    # TEST 4: Microsoft Cloud revenue
    # ------------------------------------------------------------------

    print_matching_chunks(
        enriched_chunks,
        "TEST 4: MICROSOFT CLOUD REVENUE",
        lambda chunk: (
            chunk["contains_microsoft_cloud"]
        ),
    )

    # ------------------------------------------------------------------
    # TEST 5: Total revenue
    # ------------------------------------------------------------------

    print_matching_chunks(
        enriched_chunks,
        "TEST 5: TOTAL REVENUE",
        lambda chunk: (
            chunk["contains_revenue"]
            and chunk["contains_total"]
        ),
    )

    # ------------------------------------------------------------------
    # TEST 6: Multi-year revenue chunks
    # ------------------------------------------------------------------

    print_matching_chunks(
        enriched_chunks,
        "TEST 6: MULTI-YEAR REVENUE CHUNKS",
        lambda chunk: (
            chunk["contains_revenue"]
            and len(chunk["years"]) >= 2
        ),
    )

    # ------------------------------------------------------------------
    # TEST 7: Problematic multi-year total revenue query
    # ------------------------------------------------------------------

    print_matching_chunks(
        enriched_chunks,
        "TEST 7: TOTAL REVENUE CHUNKS EXCLUDING MICROSOFT CLOUD",
        lambda chunk: (
            chunk["contains_revenue"]
            and chunk["contains_total"]
            and len(chunk["years"]) >= 2
            and not chunk["contains_microsoft_cloud"]
        ),
    )

    print("\n" + "=" * 80)
    print("REAL REPORT METADATA TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()