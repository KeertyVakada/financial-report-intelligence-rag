from ingestion import extract_text_from_pdf
from preprocessing import preprocess_pages
from chunking import create_chunks


PDF_PATH = "../data/raw/2025_AnnualReport.pdf"


# 1. Extract
pages = extract_text_from_pdf(PDF_PATH)

# 2. Preprocess
processed_pages = preprocess_pages(pages)

# 3. Chunk
chunks = create_chunks(processed_pages)


print("=" * 60)
print("CHUNKING TEST")
print("=" * 60)

print(f"Processed pages: {len(processed_pages)}")
print(f"Total chunks: {len(chunks)}")

print("\nChunk size statistics:")

chunk_sizes = [chunk["character_count"] for chunk in chunks]

print(f"Minimum chunk size: {min(chunk_sizes)}")
print(f"Maximum chunk size: {max(chunk_sizes)}")
print(
    f"Average chunk size: "
    f"{sum(chunk_sizes) / len(chunk_sizes):.0f}"
)


print("\n" + "=" * 60)
print("FIRST CHUNK")
print("=" * 60)

print(chunks[0])


print("\n" + "=" * 60)
print("FINANCIAL STATEMENT CHUNKS")
print("=" * 60)

for chunk in chunks:
    if chunk["pdf_page"] == 36:
        print("\n")
        print(chunk)


print("\n" + "=" * 60)
print("LAST CHUNK")
print("=" * 60)

print(chunks[-1])