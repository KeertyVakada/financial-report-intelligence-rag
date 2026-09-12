import json
from pathlib import Path

from rank_bm25 import BM25Okapi
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.json"


print("Loading chunks...")

chunks_path = Path(CHUNKS_PATH)

if not chunks_path.exists():
    raise FileNotFoundError(
        f"Chunks file not found: {chunks_path}"
    )
    
with open(CHUNKS_PATH, "r", encoding="utf-8") as file:
    chunks = json.load(file)

print(f"Loaded {len(chunks)} chunks.")


def tokenize(text: str) -> list[str]:
    """
    Convert text into tokens for BM25 retrieval.

    Lowercasing makes matching case-insensitive.
    """

    return text.lower().split()


print("\nPreparing BM25 corpus...")

tokenized_corpus = [
    tokenize(chunk["text"])
    for chunk in chunks
]

bm25 = BM25Okapi(tokenized_corpus)

print("BM25 index created.")


def retrieve_bm25(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve the most relevant chunks using BM25.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    tokenized_query = tokenize(query)

    scores = bm25.get_scores(tokenized_query)

    top_indices = scores.argsort()[::-1][:top_k]

    results = []

    for rank, index in enumerate(
        top_indices,
        start=1,
    ):
        chunk = chunks[index].copy()

        chunk["rank"] = rank
        chunk["bm25_score"] = float(scores[index])

        results.append(chunk)

    return results


def main():
    """
    Run an interactive BM25 retrieval test.
    """

    print("\n" + "=" * 70)
    print("BM25 FINANCIAL REPORT RETRIEVAL")
    print("=" * 70)

    print("\nEnter a question to search the annual report.")
    print("Type 'exit' to stop.\n")

    while True:

        query = input("Question: ").strip()

        if query.lower() == "exit":
            print("\nExiting BM25 test.")
            break

        if not query:
            print("Please enter a question.\n")
            continue

        results = retrieve_bm25(
            query,
            top_k=5,
        )

        print("\n" + "-" * 70)
        print("TOP 5 BM25 RESULTS")
        print("-" * 70)

        for result in results:

            print(
                f"\nRank {result['rank']} | "
                f"BM25 score: {result['bm25_score']:.4f}"
            )

            print(
                f"Chunk ID: {result['chunk_id']}"
            )

            print(
                f"PDF page: {result['pdf_page']} | "
                f"Report page: {result['report_page']}"
            )

            print("\nText:")
            print(result["text"])

        print()


if __name__ == "__main__":
    main()