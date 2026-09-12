from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from financial_evidence_retrieval import retrieve_financial_evidence
from context_builder import build_context


# -------------------------------------------------------------------
# Test question
# -------------------------------------------------------------------

question = "What was Microsoft's total revenue in fiscal year 2025?"


# -------------------------------------------------------------------
# Retrieve evidence
# -------------------------------------------------------------------

results = retrieve_financial_evidence(
    question,
    top_k=5,
)


# -------------------------------------------------------------------
# Build context
# -------------------------------------------------------------------

context = build_context(
    results,
    max_chunks=5,
)


# -------------------------------------------------------------------
# Display
# -------------------------------------------------------------------

print("=" * 80)
print("CONTEXT BUILDER TEST")
print("=" * 80)

print(f"\nQuestion:\n{question}")

print("\n" + "=" * 80)
print("BUILT CONTEXT")
print("=" * 80)

print(context)

print("\n" + "=" * 80)
print("CONTEXT BUILDER TEST COMPLETE")
print("=" * 80)