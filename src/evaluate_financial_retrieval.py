import json

from hybrid_retrieval import retrieve_hybrid
from financial_metadata import add_financial_metadata
from financial_scoring import apply_financial_scoring


QUESTIONS_PATH = "evaluation_questions.json"

CANDIDATE_COUNT = 20
FINAL_COUNT = 5


def load_questions(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def reciprocal_rank(
    results: list[dict],
    expected_chunks: list[str],
) -> float:
    """
    Calculate reciprocal rank for one question.

    Returns:
        1 / rank of the first relevant result.
        Returns 0 if no relevant result is found.
    """

    expected = set(expected_chunks)

    for rank, result in enumerate(results, start=1):
        if result["chunk_id"] in expected:
            return 1.0 / rank

    return 0.0


def evaluate():
    questions = load_questions(QUESTIONS_PATH)

    document_questions = [
        question
        for question in questions
        if question["type"] != "out_of_document"
    ]

    print("=" * 80)
    print("FINANCIAL-AWARE RETRIEVAL EVALUATION")
    print("=" * 80)

    print(
        f"\nDocument questions: "
        f"{len(document_questions)}"
    )

    print(
        f"Candidate count: "
        f"{CANDIDATE_COUNT}"
    )

    print(
        f"Final count: "
        f"{FINAL_COUNT}"
    )

    hit_at_1 = 0
    hit_at_3 = 0
    hit_at_5 = 0
    reciprocal_ranks = []

    print("\n" + "=" * 80)
    print("QUESTION RESULTS")
    print("=" * 80)

    for question in document_questions:
        query = question["question"]
        expected_chunks = question["expected_chunks"]

        candidates = retrieve_hybrid(
            query=query,
            top_k=CANDIDATE_COUNT,
        )

        enriched_candidates = add_financial_metadata(
            candidates
        )

        results = apply_financial_scoring(
            query=query,
            candidates=enriched_candidates,
            top_k=FINAL_COUNT,
        )

        ranks = []

        for rank, result in enumerate(results, start=1):
            if result["chunk_id"] in expected_chunks:
                ranks.append(rank)

        first_relevant_rank = (
            min(ranks)
            if ranks
            else None
        )

        if first_relevant_rank == 1:
            hit_at_1 += 1

        if (
            first_relevant_rank is not None
            and first_relevant_rank <= 3
        ):
            hit_at_3 += 1

        if (
            first_relevant_rank is not None
            and first_relevant_rank <= 5
        ):
            hit_at_5 += 1

        rr = reciprocal_rank(
            results=results,
            expected_chunks=expected_chunks,
        )

        reciprocal_ranks.append(rr)

        print("\n" + "-" * 80)
        print(f"{question['id']}: {query}")

        if first_relevant_rank is not None:
            print(
                f"First relevant rank: "
                f"{first_relevant_rank}"
            )
        else:
            print(
                "First relevant rank: "
                "NOT FOUND"
            )

        if results:
            top_result = results[0]

            print(
                f"Top result: "
                f"{top_result['chunk_id']}"
            )

            print(
                f"Top result financial score: "
                f"{top_result['financial_score']:.6f}"
            )

            print(
                f"Top result final score: "
                f"{top_result['final_financial_score']:.6f}"
            )

        print("\nTop 5 chunks:")

        for rank, result in enumerate(
            results,
            start=1,
        ):
            marker = (
                " <-- RELEVANT"
                if result["chunk_id"]
                in expected_chunks
                else ""
            )

            print(
                f"  {rank}. "
                f"{result['chunk_id']}"
                f"{marker}"
            )

    total = len(document_questions)

    hit_at_1_score = hit_at_1 / total
    hit_at_3_score = hit_at_3 / total
    hit_at_5_score = hit_at_5 / total
    mrr_score = sum(reciprocal_ranks) / total

    print("\n" + "=" * 80)
    print("FINAL EVALUATION RESULTS")
    print("=" * 80)

    print(
        f"\nHit@1: "
        f"{hit_at_1}/{total} "
        f"= {hit_at_1_score:.2%}"
    )

    print(
        f"Hit@3: "
        f"{hit_at_3}/{total} "
        f"= {hit_at_3_score:.2%}"
    )

    print(
        f"Hit@5: "
        f"{hit_at_5}/{total} "
        f"= {hit_at_5_score:.2%}"
    )

    print(
        f"MRR: "
        f"{mrr_score:.4f}"
    )

    print("\n" + "=" * 80)
    print("FINANCIAL-AWARE RETRIEVAL EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    evaluate()