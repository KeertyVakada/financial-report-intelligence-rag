import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from hybrid_retrieval import retrieve_hybrid
from financial_metadata import add_financial_metadata
from financial_scoring import apply_financial_scoring
from evidence_type import add_evidence_types
from evidence_scoring import apply_evidence_scoring


# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

EVALUATION_FILE = Path(__file__).resolve().parent / "evaluation_questions.json"

CANDIDATE_COUNT = 20
FINAL_COUNT = 5


# -------------------------------------------------------------------
# Load evaluation questions
# -------------------------------------------------------------------

with open(EVALUATION_FILE, "r", encoding="utf-8") as file:
    evaluation_data = json.load(file)


# -------------------------------------------------------------------
# Evaluation
# -------------------------------------------------------------------

def evaluate():

    document_questions = [
        item
        for item in evaluation_data
        if item.get("expected_chunks")
    ]

    print("=" * 80)
    print("FINANCIAL + EVIDENCE RETRIEVAL EVALUATION")
    print("=" * 80)

    print(f"\nDocument questions: {len(document_questions)}")
    print(f"Candidate count: {CANDIDATE_COUNT}")
    print(f"Final count: {FINAL_COUNT}")

    print("\n" + "=" * 80)

    hits_at_1 = 0
    hits_at_3 = 0
    hits_at_5 = 0

    reciprocal_ranks = []

    # ---------------------------------------------------------------
    # Evaluate each question
    # ---------------------------------------------------------------

    for index, item in enumerate(
        document_questions,
        start=1,
    ):

        question = item["question"]

        expected_chunks = set(
            item["expected_chunks"]
        )

        print("\n" + "-" * 80)
        print(f"Q{index:02d}: {question}")
        print("-" * 80)

        # -----------------------------------------------------------
        # Step 1: Hybrid retrieval
        # -----------------------------------------------------------

        candidates = retrieve_hybrid(
            question,
            top_k=CANDIDATE_COUNT,
        )

        # -----------------------------------------------------------
        # Step 2: Financial metadata
        # -----------------------------------------------------------

        candidates = add_financial_metadata(
            candidates
        )

        # -----------------------------------------------------------
        # Step 3: Financial scoring
        # -----------------------------------------------------------

        candidates = apply_financial_scoring(
            question,
            candidates,
        )

        # -----------------------------------------------------------
        # Step 4: Evidence type
        # -----------------------------------------------------------

        candidates = add_evidence_types(
            candidates
        )

        # -----------------------------------------------------------
        # Step 5: Evidence scoring
        # -----------------------------------------------------------

        candidates = apply_evidence_scoring(
            question,
            candidates,
        )

        # -----------------------------------------------------------
        # Final top-k results
        # -----------------------------------------------------------

        results = candidates[:FINAL_COUNT]

        # -----------------------------------------------------------
        # Determine first relevant rank
        # -----------------------------------------------------------

        first_relevant_rank = None

        for rank, result in enumerate(
            results,
            start=1,
        ):

            chunk_id = result["chunk_id"]

            if chunk_id in expected_chunks:
                first_relevant_rank = rank
                break

        # -----------------------------------------------------------
        # Calculate metrics for this question
        # -----------------------------------------------------------

        if first_relevant_rank is not None:

            if first_relevant_rank <= 1:
                hits_at_1 += 1

            if first_relevant_rank <= 3:
                hits_at_3 += 1

            if first_relevant_rank <= 5:
                hits_at_5 += 1

            reciprocal_ranks.append(
                1.0 / first_relevant_rank
            )

            print(
                f"First relevant rank: "
                f"{first_relevant_rank}"
            )

        else:

            reciprocal_ranks.append(0.0)

            print(
                "First relevant rank: NOT FOUND"
            )

        # -----------------------------------------------------------
        # Show final rankings
        # -----------------------------------------------------------

        print("\nTop results:")

        for rank, result in enumerate(
            results,
            start=1,
        ):

            relevant = (
                " <-- RELEVANT"
                if result["chunk_id"] in expected_chunks
                else ""
            )

            print(
                f"{rank}. "
                f"{result['chunk_id']} "
                f"| evidence={result.get('evidence_type')} "
                f"| score={result.get('combined_score', 0.0):.4f}"
                f"{relevant}"
            )

    # ----------------------------------------------------------------
    # Final metrics
    # ----------------------------------------------------------------

    total = len(document_questions)

    if total == 0:
        print("\nNo document questions found.")
        return

    # Convert counts into rates

    hit_at_1 = hits_at_1 / total
    hit_at_3 = hits_at_3 / total
    hit_at_5 = hits_at_5 / total

    mrr = sum(reciprocal_ranks) / total

    # ----------------------------------------------------------------
    # Final results
    # ----------------------------------------------------------------

    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    print(
        f"\nHit@1 : {hit_at_1:.4f} "
        f"({hit_at_1 * 100:.2f}%)"
    )

    print(
        f"Hit@3 : {hit_at_3:.4f} "
        f"({hit_at_3 * 100:.2f}%)"
    )

    print(
        f"Hit@5 : {hit_at_5:.4f} "
        f"({hit_at_5 * 100:.2f}%)"
    )

    print(
        f"MRR   : {mrr:.4f}"
    )

    print("\n" + "=" * 80)
    print("FINANCIAL + EVIDENCE RETRIEVAL EVALUATION COMPLETE")
    print("=" * 80)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

if __name__ == "__main__":
    evaluate()