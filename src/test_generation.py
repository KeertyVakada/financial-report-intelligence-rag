from context_builder import build_context
from generation import generate_answer


# ---------------------------------------------------------------
# Sample retrieved financial evidence
# ---------------------------------------------------------------

retrieved_chunks = [
    {
        "document": "financial_report.pdf",
        "pdf_page": 10,
        "report_page": 8,
        "evidence_type": "financial_metric",
        "chunk_id": "chunk_001",
        "text": (
            "Revenue increased from $10.2 billion in 2024 "
            "to $11.5 billion in 2025, representing an increase "
            "of approximately 12.7%."
        ),
    }
]


# ---------------------------------------------------------------
# Build context
# ---------------------------------------------------------------

context = build_context(
    retrieved_chunks,
    max_chunks=5,
)


# ---------------------------------------------------------------
# Generate answer
# ---------------------------------------------------------------

question = "What was the company's revenue in 2025?"

answer = generate_answer(
    question=question,
    context=context,
)


print("\nQUESTION:")
print(question)

print("\nANSWER:")
print(answer)