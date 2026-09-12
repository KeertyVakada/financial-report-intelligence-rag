from statistics import mean, median

from ingestion import extract_text_from_pdf
from preprocessing import preprocess_pages
from chunking import create_chunks


PDF_PATH = "../data/raw/2025_AnnualReport.pdf"


def print_separator(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------
# 1. Load and create chunks
# ---------------------------------------------------------

pages = extract_text_from_pdf(PDF_PATH)
processed_pages = preprocess_pages(pages)
chunks = create_chunks(processed_pages)


# ---------------------------------------------------------
# 2. Basic statistics
# ---------------------------------------------------------

sizes = [chunk["character_count"] for chunk in chunks]

print_separator("CHUNK QUALITY REPORT")

print(f"Original PDF pages : {len(pages)}")
print(f"Processed pages    : {len(processed_pages)}")
print(f"Total chunks       : {len(chunks)}")

print("\nChunk size statistics:")
print(f"Minimum size       : {min(sizes)} characters")
print(f"Maximum size       : {max(sizes)} characters")
print(f"Average size       : {mean(sizes):.0f} characters")
print(f"Median size        : {median(sizes):.0f} characters")


# ---------------------------------------------------------
# 3. Small chunks
# ---------------------------------------------------------

print_separator("CHUNKS BELOW 200 CHARACTERS")

small_chunks = [
    chunk
    for chunk in chunks
    if chunk["character_count"] < 200
]

print(f"Number of small chunks: {len(small_chunks)}")

for chunk in small_chunks:
    print(
        f"\n{chunk['chunk_id']} | "
        f"{chunk['character_count']} chars | "
        f"PDF page {chunk['pdf_page']} | "
        f"Report page {chunk['report_page']}"
    )

    print("-" * 70)
    print(chunk["text"])


# ---------------------------------------------------------
# 4. Large chunks
# ---------------------------------------------------------

print_separator("CHUNKS ABOVE 1200 CHARACTERS")

large_chunks = [
    chunk
    for chunk in chunks
    if chunk["character_count"] > 1200
]

print(f"Number of large chunks: {len(large_chunks)}")

for chunk in large_chunks:
    print(
        f"\n{chunk['chunk_id']} | "
        f"{chunk['character_count']} chars | "
        f"PDF page {chunk['pdf_page']} | "
        f"Report page {chunk['report_page']}"
    )

    print("-" * 70)
    print(chunk["text"][:1000])

    if len(chunk["text"]) > 1000:
        print("\n[Showing first 1000 characters only]")


# ---------------------------------------------------------
# 5. Representative chunks
# ---------------------------------------------------------

print_separator("REPRESENTATIVE CHUNK SAMPLES")


sample_pages = [2, 9, 36, 68, 72, 79]

for pdf_page in sample_pages:

    page_chunks = [
        chunk
        for chunk in chunks
        if chunk["pdf_page"] == pdf_page
    ]

    if not page_chunks:
        print(f"\nPDF page {pdf_page}: No chunks found.")
        continue

    print(
        f"\nPDF PAGE {pdf_page} "
        f"({len(page_chunks)} chunk(s))"
    )

    print("-" * 70)

    for chunk in page_chunks[:2]:

        print(
            f"\nChunk ID      : {chunk['chunk_id']}"
        )

        print(
            f"Report page   : {chunk['report_page']}"
        )

        print(
            f"Character count: {chunk['character_count']}"
        )

        print("\nText:")
        print(chunk["text"])


# ---------------------------------------------------------
# 6. Chunks per PDF page
# ---------------------------------------------------------

print_separator("CHUNKS PER PDF PAGE")

chunks_per_page = {}

for chunk in chunks:
    pdf_page = chunk["pdf_page"]

    chunks_per_page[pdf_page] = (
        chunks_per_page.get(pdf_page, 0) + 1
    )

for pdf_page, count in chunks_per_page.items():
    print(
        f"PDF page {pdf_page:>2}: "
        f"{count} chunk(s)"
    )


# ---------------------------------------------------------
# 7. Final summary
# ---------------------------------------------------------

print_separator("QUALITY SUMMARY")

print(f"Total chunks              : {len(chunks)}")
print(f"Chunks < 200 chars       : {len(small_chunks)}")
print(f"Chunks > 1200 chars      : {len(large_chunks)}")

print("\nChunking quality report completed successfully.")