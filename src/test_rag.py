from financial_evidence_retrieval import retrieve_financial_evidence
from reranker import rerank
from context_builder import build_context
from generation import generate_answer


CANDIDATE_COUNT = 20
FINAL_COUNT = 5


TEST_QUESTIONS = [
    "What was Microsoft's total revenue in fiscal year 2025?",
    
    "What was Microsoft's Gaming revenue in fiscal year 2025?",
    
    "What was Microsoft's net cash from operations in fiscal year 2025?",
    
    "Which Microsoft segment had the highest revenue in fiscal year 2025?",
    
    "Why did Gaming revenue increase in fiscal year 2025?",
    
    "What were Microsoft's total revenues in fiscal years 2025, 2024, and 2023?",
]


def answer_question(question: str) -> str:

    # ---------------------------------------------------------
    # Step 1: Retrieve financial candidates
    # ---------------------------------------------------------

    retrieved_candidates = retrieve_financial_evidence(
        query=question,
        top_k=CANDIDATE_COUNT
    )

    # ---------------------------------------------------------
    # Step 2: Cross-encoder + financial-aware reranking
    # ---------------------------------------------------------

    retrieved_chunks = rerank(
        query=question,
        candidates=retrieved_candidates,
        top_k=FINAL_COUNT
    )

    # ---------------------------------------------------------
    # Step 3: Build context
    # ---------------------------------------------------------

    context = build_context(
        retrieved_chunks=retrieved_chunks,
        max_chunks=FINAL_COUNT
    )

    # ---------------------------------------------------------
    # Step 4: Generate answer
    # ---------------------------------------------------------

    answer = generate_answer(
        question=question,
        context=context
    )

    return answer


def main():

    print("=" * 80)
    print("FINANCIAL REPORT RAG - TEST SUITE")
    print("=" * 80)

    print(f"\nRunning {len(TEST_QUESTIONS)} test questions...\n")

    for index, question in enumerate(TEST_QUESTIONS, start=1):

        print("\n" + "=" * 80)
        print(f"TEST {index}/{len(TEST_QUESTIONS)}")
        print("=" * 80)

        print("\nQuestion:")
        print(question)

        try:

            answer = answer_question(question)

            print("\nAnswer:")
            print(answer)

        except Exception as e:

            print("\nERROR:")
            print(type(e).__name__, "-", e)

    print("\n" + "=" * 80)
    print("RAG TEST SUITE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()