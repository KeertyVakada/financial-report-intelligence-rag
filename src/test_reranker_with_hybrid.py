from hybrid_retrieval import retrieve_hybrid
from reranker import rerank


TEST_QUESTIONS = [
    "What was Microsoft's Gaming revenue in fiscal year 2025?",
    "What were Microsoft's total assets as of June 30, 2025?",
    "What were Microsoft's total revenues in fiscal years 2025, 2024, and 2023?",
]


CANDIDATE_COUNT = 20
FINAL_COUNT = 5


def main():
    print("=" * 80)
    print("HYBRID + CROSS-ENCODER RERANKER TEST")
    print("=" * 80)

    for question_number, question in enumerate(
        TEST_QUESTIONS,
        start=1,
    ):

        print("\n" + "=" * 80)
        print(f"QUESTION {question_number}")
        print("=" * 80)

        print(f"\nQuestion: {question}")

        print(
            f"\nRetrieving top {CANDIDATE_COUNT} "
            "hybrid candidates..."
        )

        candidates = retrieve_hybrid(
            query=question,
            top_k=CANDIDATE_COUNT,
        )

        print(
            f"Retrieved {len(candidates)} candidates."
        )

        print("\nTop 5 BEFORE reranking:")

        for candidate in candidates[:5]:
            print(
                f"  Rank {candidate['rank']} | "
                f"RRF {candidate['rrf_score']:.6f} | "
                f"Page {candidate['report_page']} | "
                f"{candidate['chunk_id']}"
            )

        print("\nApplying cross-encoder reranker...")

        reranked_results = rerank(
            query=question,
            candidates=candidates,
            top_k=FINAL_COUNT,
        )

        print("\nTop 5 AFTER reranking:")

        for result in reranked_results:
            print(
                f"  Rank {result['reranker_rank']} | "
                f"Reranker {result['reranker_score']:.4f} | "
                f"RRF {result['rrf_score']:.6f} | "
                f"Page {result['report_page']} | "
                f"{result['chunk_id']}"
            )

        print("\nTop result text:")
        print("-" * 80)
        print(reranked_results[0]["text"])

    print("\n" + "=" * 80)
    print("RERANKER + HYBRID TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()