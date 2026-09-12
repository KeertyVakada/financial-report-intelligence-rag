from ingestion import extract_text_from_pdf


PDF_PATH = "../data/raw/2025_AnnualReport.pdf"


pages = extract_text_from_pdf(PDF_PATH)

total_pages = len(pages)

empty_pages = [
    page["page_number"]
    for page in pages
    if not page["text"]
]

short_pages = [
    (page["page_number"], len(page["text"]))
    for page in pages
    if 0 < len(page["text"]) < 200
]

total_characters = sum(len(page["text"]) for page in pages)

non_empty_pages = total_pages - len(empty_pages)

average_characters = (
    total_characters / non_empty_pages
    if non_empty_pages
    else 0
)


print("=" * 60)
print("DOCUMENT INSPECTION")
print("=" * 60)

print(f"Total pages: {total_pages}")
print(f"Non-empty pages: {non_empty_pages}")
print(f"Empty pages: {len(empty_pages)}")
print(f"Total characters: {total_characters:,}")
print(f"Average characters per non-empty page: {average_characters:,.0f}")

print("\nEmpty pages:")
print(empty_pages)

print("\nShort pages (< 200 characters):")
print(short_pages)

print("\nText length by page:")
for page in pages:
    print(
        f"Page {page['page_number']:>2}: "
        f"{len(page['text']):>6,} characters"
    )