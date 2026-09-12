from hybrid_retrieval import retrieve_hybrid
from financial_metadata import add_financial_metadata
from financial_scoring import apply_financial_scoring


CANDIDATE_COUNT = 20
FINAL_COUNT = 5


TEST_QUESTIONS = [
    "What was Microsoft's total revenue in fiscal year 2025?",
    "What were Microsoft's total assets as of June 30, 2025?",
    "What was Microsoft's net cash from operations in fiscal year 2025?",
    "What was Microsoft's Gaming revenue in fiscal year 2025?",
    "What was Microsoft's Microsoft Cloud revenue in fiscal year 2025?",
    "What were Microsoft's total revenues in fiscal years 2025, 2024, and 2023?",
    "Which Microsoft segment had the highest revenue in fiscal year 2025?",
]


def print_results(
    query: str,
    results: list[dict],
) -> None:
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    for result in results:
        print("\n" + "-" * 80)

        print(
            f"Financial rank: "
            f"{result['financial_rank']}"
        )

        print(
            f"Chunk: "
            f"{result['chunk_id']}"
        )

        print(
            f"PDF page: "
            f"{result['pdf_page']}"
        )

        print(
            f"Report page: "
            f"{result['report_page']}"
        )

        print(
            f"Financial section: "
            f"{result.get('financial_section')}"
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
            f"Final financial score: "
            f"{result.get('final_financial_score', 0.0):.6f}"
        )

        print(
            f"Contains total: "
            f"{result.get('contains_total')}"
        )

        print(
            f"Contains revenue: "
            f"{result.get('contains_revenue')}"
        )

        print(
            f"Contains Microsoft Cloud: "
            f"{result.get('contains_microsoft_cloud')}"
        )

        print(
            f"Contains assets: "
            f"{result.get('contains_assets')}"
        )

        print(
            f"Contains cash flow: "
            f"{result.get('contains_cash_flow')}"
        )

        print(
            f"Contains segment: "
            f"{result.get('contains_segment')}"
        )

        print("\nText preview:")
        print(result["text"][:500])


def main():
    print("=" * 80)
    print("FINANCIAL-AWARE RETRIEVAL TEST")
    print("=" * 80)

    for question_number, query in enumerate(
        TEST_QUESTIONS,
        start=1,
    ):
        print("\n" + "=" * 80)
        print(f"TEST QUESTION {question_number}")
        print("=" * 80)

        # ----------------------------------------------------------
        # Step 1: Hybrid retrieval
        # ----------------------------------------------------------

        candidates = retrieve_hybrid(
            query=query,
            top_k=CANDIDATE_COUNT,
        )

        # ----------------------------------------------------------
        # Step 2: Add financial metadata
        # ----------------------------------------------------------

        enriched_candidates = add_financial_metadata(
            candidates
        )

        # ----------------------------------------------------------
        # Step 3: Financial-aware scoring
        # ----------------------------------------------------------

        results = apply_financial_scoring(
            query=query,
            candidates=enriched_candidates,
            top_k=FINAL_COUNT,
        )

        # ----------------------------------------------------------
        # Step 4: Display results
        # ----------------------------------------------------------

        print_results(
            query=query,
            results=results,
        )

    print("\n" + "=" * 80)
    print("FINANCIAL-AWARE RETRIEVAL TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()