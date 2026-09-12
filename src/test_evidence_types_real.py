from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))

from ingestion import extract_text_from_pdf
from preprocessing import preprocess_pages
from chunking import create_chunks
from financial_metadata import add_financial_metadata
from evidence_type import add_evidence_types


PDF_PATH = "../data/raw/2025_AnnualReport.pdf"


print("=" * 80)
print("REAL REPORT EVIDENCE TYPE TEST")
print("=" * 80)


# -------------------------------------------------------------------
# 1. Extract PDF
# -------------------------------------------------------------------

pages = extract_text_from_pdf(PDF_PATH)

print(f"\nOriginal PDF pages: {len(pages)}")


# -------------------------------------------------------------------
# 2. Preprocess
# -------------------------------------------------------------------

processed_pages = preprocess_pages(pages)

print(f"Non-empty pages: {len(processed_pages)}")


# -------------------------------------------------------------------
# 3. Create chunks
# -------------------------------------------------------------------

chunks = create_chunks(processed_pages)

print(f"Chunks created: {len(chunks)}")


# -------------------------------------------------------------------
# 4. Add financial metadata
# -------------------------------------------------------------------

chunks = add_financial_metadata(chunks)


# -------------------------------------------------------------------
# 5. Detect evidence types
# -------------------------------------------------------------------

chunks = add_evidence_types(chunks)


# -------------------------------------------------------------------
# 6. Count evidence types
# -------------------------------------------------------------------

counts = {}

for chunk in chunks:
    evidence_type = chunk["evidence_type"]
    counts[evidence_type] = counts.get(evidence_type, 0) + 1


print("\n" + "=" * 80)
print("EVIDENCE TYPE DISTRIBUTION")
print("=" * 80)

for evidence_type, count in sorted(counts.items()):
    print(f"{evidence_type:25s}: {count}")


# -------------------------------------------------------------------
# 7. Show examples from each evidence type
# -------------------------------------------------------------------

print("\n" + "=" * 80)
print("EXAMPLES")
print("=" * 80)


shown_types = set()

for chunk in chunks:

    evidence_type = chunk["evidence_type"]

    if evidence_type in shown_types:
        continue

    shown_types.add(evidence_type)

    print("\n" + "-" * 80)
    print(f"Evidence type : {evidence_type}")
    print(f"Chunk ID      : {chunk['chunk_id']}")
    print(f"PDF page     : {chunk['pdf_page']}")
    print(f"Report page  : {chunk['report_page']}")

    print("\nText preview:")
    print(chunk["text"][:700])

    if len(shown_types) == len(counts):
        break


print("\n" + "=" * 80)
print("REAL REPORT EVIDENCE TYPE TEST COMPLETE")
print("=" * 80)