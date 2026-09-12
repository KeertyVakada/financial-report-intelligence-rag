import json
from pathlib import Path


CHUNKS_PATH = "../data/processed/chunks.json"


def main():
    """Find chunks containing key financial statement terms."""

    chunks_path = Path(CHUNKS_PATH)

    with open(chunks_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    search_terms = [
        "Total assets",
        "Net cash from operations",
    ]

    print("=" * 80)
    print("FINANCIAL STATEMENT TERM SEARCH")
    print("=" * 80)

    for term in search_terms:

        print("\n" + "=" * 80)
        print(f"SEARCH TERM: {term}")
        print("=" * 80)

        matches = [
            chunk
            for chunk in chunks
            if term.lower() in chunk["text"].lower()
        ]

        print(f"\nFound {len(matches)} matching chunks.")

        for chunk in matches:

            print("\n" + "-" * 80)

            print(
                f"Chunk ID    : {chunk['chunk_id']}"
            )

            print(
                f"PDF page    : {chunk['pdf_page']}"
            )

            print(
                f"Report page : {chunk['report_page']}"
            )

            print(
                f"Characters  : {chunk['character_count']}"
            )

            print("\nTEXT:")
            print(chunk["text"])


if __name__ == "__main__":
    main()