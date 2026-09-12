from ingestion import extract_text_from_pdf
from preprocessing import preprocess_pages
from chunking import create_chunks


PDF_PATH = "../data/raw/2025_AnnualReport.pdf"


pages = extract_text_from_pdf(PDF_PATH)
processed_pages = preprocess_pages(pages)
chunks = create_chunks(processed_pages)


sizes = [chunk["character_count"] for chunk in chunks]


print("=" * 60)
print("CHUNK VALIDATION")
print("=" * 60)

print(f"Total chunks: {len(chunks)}")
print(f"Minimum size: {min(sizes)}")
print(f"Maximum size: {max(sizes)}")

print("\nChunks > 1200 characters:")
print("-" * 60)

for chunk in chunks:
    if chunk["character_count"] > 1200:
        print(
            f"{chunk['chunk_id']} | "
            f"{chunk['character_count']} chars | "
            f"PDF page {chunk['pdf_page']}"
        )


print("\nChunks < 200 characters:")
print("-" * 60)

for chunk in chunks:
    if chunk["character_count"] < 200:
        print(
            f"{chunk['chunk_id']} | "
            f"{chunk['character_count']} chars | "
            f"PDF page {chunk['pdf_page']}"
        )
        print(repr(chunk["text"]))
        print()