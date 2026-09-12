import json
from pathlib import Path

from bm25_retrieval import retrieve_bm25


QUESTIONS_PATH = "evaluation_questions.json"
TOP_K = 20


def load_questions() -> list[dict]:
    """Load retrieval evaluation questions."""

    questions_path = Path(QUESTIONS_PATH)

    if not questions_path.exists():
        raise FileNotFoundError(
            f"Evaluation questions file not found: {questions_path}"
        )

    with open(questions_path, "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_question(question: dict) -> dict:
    """Evaluate BM25 retrieval for one question."""

    results = retrieve_bm25(
        question["question"],
        top_k=TOP_K,
    )

    retrieved_chunk_ids = [
        result["chunk_id"]
        for result in results
    ]

    expected_chunks = question["expected_chunks"]

    # Out-of-document question
    if not expected_chunks:
        return {
            "id": question["id"],
            "question": question["question"],
            "type": question["type"],
            "expected_chunks": [],
            "retrieved_chunks": retrieved_chunk_ids,
            "hit_at_1": False,
            "hit_at_3": False,
            "hit_at_5": False,
            "reciprocal_rank": 0.0,
            "first_match_rank": None,
            "top_score": results[0]["bm25_score"],
            "results": results,
        }

    matched_ranks = []

    for result in results:
        if result["chunk_id"] in expected_chunks:
            matched_ranks.append(result["rank"])

    if matched_ranks:
        first_match_rank = min(matched_ranks)

        hit_at_1 = first_match_rank <= 1
        hit_at_3 = first_match_rank <= 3
        hit_at_5 = first_match_rank <= 5

        reciprocal_rank = 1 / first_match_rank

    else:
        first_match_rank = None
        hit_at_1 = False
        hit_at_3 = False
        hit_at_5 = False
        reciprocal_rank = 0.0

    return {
        "id": question["id"],
        "question": question["question"],
        "type": question["type"],
        "expected_chunks": expected_chunks,
        "retrieved_chunks": retrieved_chunk_ids,
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "hit_at_5": hit_at_5,
        "reciprocal_rank": reciprocal_rank,
        "first_match_rank": first_match_rank,
        "top_score": results[0]["bm25_score"],
        "results": results,
    }


def print_result(result: dict) -> None:
    """Print BM25 evaluation result."""

    print("\n" + "-" * 80)

    print(
        f"{result['id']} | "
        f"Type: {result['type']}"
    )

    print(f"Question: {result['question']}")

    print(
        f"Top BM25 score: "
        f"{result['top_score']:.4f}"
    )

    if not result["expected_chunks"]:

        print("Result: OUT-OF-DOCUMENT TEST")

    else:

        print(
            f"Hit@1: "
            f"{'YES' if result['hit_at_1'] else 'NO'}"
        )

        print(
            f"Hit@3: "
            f"{'YES' if result['hit_at_3'] else 'NO'}"
        )

        print(
            f"Hit@5: "
            f"{'YES' if result['hit_at_5'] else 'NO'}"
        )

        if result["first_match_rank"] is not None:

            print(
                f"First relevant chunk rank: "
                f"{result['first_match_rank']}"
            )

            print(
                f"Reciprocal rank: "
                f"{result['reciprocal_rank']:.4f}"
            )

        else:

            print("First relevant chunk rank: NOT FOUND")
            print("Reciprocal rank: 0.0000")

    print("\nTop retrieved chunks:")

    for item in result["results"]:

        print(
            f"  Rank {item['rank']} | "
            f"Score {item['bm25_score']:.4f} | "
            f"Page {item['report_page']} | "
            f"{item['chunk_id']}"
        )


def main():
    """Run complete BM25 evaluation."""

    print("=" * 80)
    print("BM25 FINANCIAL REPORT RETRIEVAL EVALUATION")
    print("=" * 80)

    questions = load_questions()

    print(
        f"\nLoaded {len(questions)} evaluation questions."
    )

    results = []

    for question in questions:

        result = evaluate_question(question)

        results.append(result)

        print_result(result)

    document_questions = [
        result
        for result in results
        if result["expected_chunks"]
    ]

    out_of_document_questions = [
        result
        for result in results
        if not result["expected_chunks"]
    ]

    total = len(document_questions)

    hit_at_1 = sum(
        result["hit_at_1"]
        for result in document_questions
    )

    hit_at_3 = sum(
        result["hit_at_3"]
        for result in document_questions
    )

    hit_at_5 = sum(
        result["hit_at_5"]
        for result in document_questions
    )

    mean_reciprocal_rank = (
        sum(
            result["reciprocal_rank"]
            for result in document_questions
        )
        / total
        if total
        else 0.0
    )

    print("\n" + "=" * 80)
    print("BM25 EVALUATION SUMMARY")
    print("=" * 80)

    print(
        f"\nDocument questions : {total}"
    )

    if total:

        print(
            f"Hit@1              : "
            f"{hit_at_1}/{total} "
            f"({hit_at_1 / total * 100:.2f}%)"
        )

        print(
            f"Hit@3              : "
            f"{hit_at_3}/{total} "
            f"({hit_at_3 / total * 100:.2f}%)"
        )

        print(
            f"Hit@5              : "
            f"{hit_at_5}/{total} "
            f"({hit_at_5 / total * 100:.2f}%)"
        )

        print(
            f"MRR                : "
            f"{mean_reciprocal_rank:.4f}"
        )

    print(
        f"\nOut-of-document questions: "
        f"{len(out_of_document_questions)}"
    )

    if out_of_document_questions:

        print(
            "\nTop BM25 scores for "
            "out-of-document questions:"
        )

        for result in out_of_document_questions:

            print(
                f"  {result['id']} | "
                f"{result['top_score']:.4f} | "
                f"{result['question']}"
            )

    print("\n" + "=" * 80)
    print("BM25 evaluation complete.")
    print("=" * 80)


if __name__ == "__main__":
    main()