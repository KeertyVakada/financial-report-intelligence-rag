from financial_evidence_retrieval import retrieve_financial_evidence
from reranker import rerank
from context_builder import build_context
from generation import generate_answer
import re

CANDIDATE_COUNT = 20
FINAL_COUNT = 5

EVALUATION_QUESTIONS = [
    {
        "id": 1,
        "question": "What was Microsoft's total revenue in fiscal year 2025?",
        "expected": "$281,724 million",
    },
    {
        "id": 2,
        "question": "What was Microsoft's Gaming revenue in fiscal year 2025?",
        "expected": "$23,455 million",
    },
    {
        "id": 3,
        "question": "What was Microsoft's net cash from operations in fiscal year 2025?",
        "expected": "$136.2 billion",
    },
    {
        "id": 4,
        "question": "Which Microsoft segment had the highest revenue in fiscal year 2025?",
        "expected": "Productivity and Business Processes — $120,810 million",
    },
    {
        "id": 5,
        "question": "Why did Gaming revenue increase in fiscal year 2025?",
        "expected": "Growth in Xbox content and services, driven by the Activision Blizzard acquisition and Xbox Game Pass, partially offset by lower Xbox hardware revenue.",
    },
    {
        "id": 6,
        "question": "What were Microsoft's total revenues in fiscal years 2025, 2024, and 2023?",
        "expected": "$281,724 million; $245,122 million; $211,915 million",
    },

    # ---------------------------------------------------------
    # Additional direct financial questions
    # ---------------------------------------------------------

    {
        "id": 7,
        "question": "What was Microsoft's net income in fiscal year 2025?",
        "expected": "$101,832 million",
    },
    {
        "id": 8,
        "question": "What was Microsoft's gross margin in fiscal year 2025?",
        "expected": "$193,893 million",
    },
    {
        "id": 9,
        "question": "What was Microsoft's operating income in fiscal year 2025?",
        "expected": "$128,528 million",
    },
    {
        "id": 10,
        "question": "What was Microsoft's diluted earnings per share in fiscal year 2025?",
        "expected": "$13.64",
    },

    # ---------------------------------------------------------
    # Segment questions
    # ---------------------------------------------------------

    {
        "id": 11,
        "question": "What was the revenue of the Intelligent Cloud segment in fiscal year 2025?",
        "expected": "$106,265 million",
    },
    {
        "id": 12,
        "question": "What was the revenue of the More Personal Computing segment in fiscal year 2025?",
        "expected": "$54,649 million",
    },
    {
        "id": 13,
        "question": "What was the revenue of Productivity and Business Processes in fiscal year 2025?",
        "expected": "$120,810 million",
    },

    # ---------------------------------------------------------
    # Product / service questions
    # ---------------------------------------------------------

    {
        "id": 14,
        "question": "What was Microsoft's Server products and cloud services revenue in fiscal year 2025?",
        "expected": "$98,435 million",
    },
    {
        "id": 15,
        "question": "What was Microsoft's LinkedIn revenue in fiscal year 2025?",
        "expected": "$17,812 million",
    },
    {
        "id": 16,
        "question": "What was Microsoft's Dynamics products and cloud services revenue in fiscal year 2025?",
        "expected": "$7,827 million",
    },

    # ---------------------------------------------------------
    # Comparison questions
    # ---------------------------------------------------------

    {
        "id": 17,
        "question": "How much did Microsoft's total revenue increase from fiscal year 2024 to fiscal year 2025?",
        "expected": "$36.6 billion",
    },
    {
        "id": 18,
        "question": "What was Microsoft's Microsoft Cloud revenue in fiscal year 2025?",
        "expected": "$168.9 billion",
    },

    # ---------------------------------------------------------
    # Multi-year questions
    # ---------------------------------------------------------

    {
        "id": 19,
        "question": "What was Microsoft's Gaming revenue in fiscal years 2025, 2024, and 2023?",
        "expected": "$23,455 million; $21,503 million; $15,466 million",
    },
    {
        "id": 20,
        "question": "What was Microsoft's LinkedIn revenue in fiscal years 2025, 2024, and 2023?",
        "expected": "$17,812 million; $16,372 million; $14,989 million",
    },
]



def run_rag(question: str) -> tuple[str, list[dict]]:

    candidates = retrieve_financial_evidence(
        query=question,
        top_k=CANDIDATE_COUNT
    )

    retrieved_chunks = rerank(
        query=question,
        candidates=candidates,
        top_k=FINAL_COUNT
    )

    context = build_context(
        retrieved_chunks=retrieved_chunks,
        max_chunks=FINAL_COUNT
    )

    answer = generate_answer(
        question=question,
        context=context
    )

    return answer, retrieved_chunks


import re


def normalize_text(text: str) -> str:
    """
    Normalize text so that small formatting differences
    do not affect evaluation.
    """

    text = text.lower()

    # Normalize different Unicode spaces
    text = text.replace("\u202f", " ")
    text = text.replace("\u00a0", " ")

    # Remove commas for easier numeric comparison
    text = text.replace(",", "")

    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def evaluate_answer(answer: str, expected: str) -> bool:

    answer_normalized = normalize_text(answer)
    expected_normalized = normalize_text(expected)

    # ---------------------------------------------------------
    # Extract expected numeric values
    # ---------------------------------------------------------

    expected_numbers = re.findall(
        r"\$?\d+(?:\.\d+)?",
        expected_normalized
    )

    # ---------------------------------------------------------
    # Check that every expected number appears
    # ---------------------------------------------------------

    for number in expected_numbers:

        number_clean = number.replace("$", "")

        if number_clean not in answer_normalized:
            return False

    # ---------------------------------------------------------
    # Segment question
    # ---------------------------------------------------------

    if "productivity and business processes" in expected_normalized:

        return (
            "productivity and business processes"
            in answer_normalized
            and "120810" in answer_normalized
        )

    # ---------------------------------------------------------
    # Gaming explanation
    # ---------------------------------------------------------

    if "activision blizzard" in expected_normalized:

        required_terms = [
            "activision",
            "xbox",
        ]

        return all(
            term in answer_normalized
            for term in required_terms
        )

    return True

def main():

    print("=" * 90)
    print("FINANCIAL REPORT RAG - EVALUATION")
    print("=" * 90)

    passed = 0
    failed = 0

    results = []

    for item in EVALUATION_QUESTIONS:

        question_id = item["id"]
        question = item["question"]
        expected = item["expected"]

        print("\n" + "=" * 90)
        print(f"TEST {question_id}/{len(EVALUATION_QUESTIONS)}")
        print("=" * 90)

        print("\nQuestion:")
        print(question)

        try:

            answer, chunks = run_rag(question)

            is_correct = evaluate_answer(
                answer,
                expected
            )

            status = "PASS" if is_correct else "FAIL"

            if is_correct:
                passed += 1
            else:
                failed += 1

            print("\nExpected:")
            print(expected)

            print("\nGenerated Answer:")
            print(answer)

            print("\nResult:")
            print(status)

            print("\nTop Evidence:")

            for rank, chunk in enumerate(chunks, start=1):

                print(
                    f"{rank}. "
                    f"{chunk.get('chunk_id')} | "
                    f"Page {chunk.get('report_page')} | "
                    f"{chunk.get('evidence_type')}"
                )

            results.append({
                "id": question_id,
                "status": status,
            })

        except Exception as e:

            failed += 1

            print("\nERROR:")
            print(type(e).__name__, "-", e)

            results.append({
                "id": question_id,
                "status": "ERROR",
            })

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------

    total = len(EVALUATION_QUESTIONS)

    accuracy = (passed / total) * 100

    print("\n\n" + "=" * 90)
    print("EVALUATION SUMMARY")
    print("=" * 90)

    print(f"\nTotal tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print(f"Accuracy    : {accuracy:.1f}%")

    print("\nResults:")

    for result in results:

        print(
            f"Test {result['id']}: "
            f"{result['status']}"
        )

    print("\n" + "=" * 90)
    print("EVALUATION COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()