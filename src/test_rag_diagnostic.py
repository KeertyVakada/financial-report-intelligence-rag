from routed_retrieval import retrieve_routed
from context_builder import build_context
from generation import generate_answer


QUESTIONS = [
    "What was Microsoft's total revenue in fiscal year 2025?",
    
    "How much did Microsoft's revenue increase from fiscal year 2024 to 2025?",
    
    "Which Microsoft segment had the highest revenue in fiscal year 2025?",
    
    "What were Microsoft's revenues in fiscal years 2023, 2024, and 2025?",
    
    "What is Microsoft's stock price today?",
]


def answer_question(question: str):

    retrieved_chunks = retrieve_routed(
        query=question,
        top_k=5,
    )

    context = build_context(
        retrieved_chunks=retrieved_chunks,
        max_chunks=5,
    )

    answer = generate_answer(
        question=question,
        context=context,
    )

    return retrieved_chunks, context, answer


def main():

    print("=" * 80)
    print("FINANCIAL REPORT RAG - QUALITY TEST")
    print("=" * 80)

    for number, question in enumerate(QUESTIONS, start=1):

        print("\n" + "=" * 80)
        print(f"QUESTION {number}")
        print("=" * 80)

        print(f"\nQuestion:\n{question}")

        retrieved_chunks, context, answer = answer_question(
            question
        )

        print("\nRetrieved evidence:")

        for i, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):

            print(
                f"\nEvidence {i}"
            )

            print(
                f"Rank: {chunk.get('routing_rank')}"
            )

            print(
                f"Page: {chunk.get('report_page')}"
            )

            print(
                f"Chunk: {chunk.get('chunk_id')}"
            )

            print(
                f"Score: {chunk.get('routing_score', 0):.6f}"
            )

            print(
                f"Text: {chunk.get('text', '')[:500]}"
            )

        print("\nFINAL ANSWER:")
        print(answer)

    print("\n" + "=" * 80)
    print("QUALITY TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()