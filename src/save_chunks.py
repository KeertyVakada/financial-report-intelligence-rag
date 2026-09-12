import json
from pathlib import Path

from ingestion import extract_text_from_pdf
from preprocessing import preprocess_pages
from chunking import create_chunks


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PDF_PATH = "../data/raw/2025_AnnualReport.pdf"
OUTPUT_PATH = "../data/processed/chunks.json"


# ---------------------------------------------------------
# 1. Extract PDF text
# ---------------------------------------------------------

print("Loading PDF...")

pages = extract_text_from_pdf(PDF_PATH)

print(f"Extracted {len(pages)} PDF pages.")


# ---------------------------------------------------------
# 2. Preprocess pages
# ---------------------------------------------------------

print("Preprocessing pages...")

processed_pages = preprocess_pages(pages)

print(f"Processed {len(processed_pages)} non-empty pages.")


# ---------------------------------------------------------
# 3. Create chunks
# ---------------------------------------------------------

print("Creating chunks...")

chunks = create_chunks(
    processed_pages,
    max_chars=1200,
    overlap_chars=200,
    min_chars=200,
)

print(f"Created {len(chunks)} chunks.")


# ---------------------------------------------------------
# 4. Create output directory
# ---------------------------------------------------------

output_path = Path(OUTPUT_PATH)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# 5. Save chunks as JSON
# ---------------------------------------------------------

with open(
    output_path,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        chunks,
        file,
        indent=2,
        ensure_ascii=False,
    )


# ---------------------------------------------------------
# 6. Verify saved file
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("CHUNKS SAVED SUCCESSFULLY")
print("=" * 60)

print(f"Output file : {output_path}")
print(f"Total chunks: {len(chunks)}")

print("\nFirst chunk:")
print("-" * 60)
print(json.dumps(chunks[0], indent=2, ensure_ascii=False))

print("\nLast chunk:")
print("-" * 60)
print(json.dumps(chunks[-1], indent=2, ensure_ascii=False))