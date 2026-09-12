from financial_evidence_retrieval import retrieve_financial_evidence
from reranker import rerank


QUESTION = "Which Microsoft segment had the highest revenue in fiscal year 2025?"

CANDIDATE_COUNT = 20
FINAL_COUNT = 5


def main():

    print("=" * 100)
    print("SEGMENT RETRIEVAL DEBUG")
    print("=" * 100)

    print(f"\nQuestion:\n{QUESTION}\n")

    # ---------------------------------------------------------
    # Step 1: Financial retrieval
    # ---------------------------------------------------------

    candidates = retrieve_financial_evidence(
        query=QUESTION,
        top_k=CANDIDATE_COUNT
    )

    print("\n" + "=" * 100)
    print(f"FINANCIAL RETRIEVAL RESULTS ({len(candidates)} candidates)")
    print("=" * 100)

    for i, chunk in enumerate(candidates, start=1):

        print(f"\n--- Candidate {i} ---")

        print("Chunk ID:", chunk.get("chunk_id"))
        print("PDF Page:", chunk.get("page"))
        print("Report Page:", chunk.get("report_page"))

        print("Base Score:", chunk.get("score"))
        print("Financial Score:", chunk.get("financial_score"))
        print("Evidence Score:", chunk.get("evidence_score"))
        print("Evidence Type:", chunk.get("evidence_type"))

        print("\nText:")
        print(chunk.get("text", "")[:1000])

    # ---------------------------------------------------------
    # Step 2: Cross-encoder reranking
    # ---------------------------------------------------------

    reranked = rerank(
        query=QUESTION,
        candidates=candidates,
        top_k=FINAL_COUNT
    )

    print("\n" + "=" * 100)
    print(f"FINAL RERANKED RESULTS ({len(reranked)} chunks)")
    print("=" * 100)

    for i, chunk in enumerate(reranked, start=1):

        print(f"\n--- Final Rank {i} ---")

        print("Chunk ID:", chunk.get("chunk_id"))
        print("PDF Page:", chunk.get("page"))
        print("Report Page:", chunk.get("report_page"))

        print("Reranker Score:", chunk.get("reranker_score"))
        print("Financial Score:", chunk.get("financial_score"))
        print("Evidence Score:", chunk.get("evidence_score"))
        print("Evidence Type:", chunk.get("evidence_type"))

        print("\nText:")
        print(chunk.get("text", "")[:1500])

    print("\n" + "=" * 100)
    print("DEBUG COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()