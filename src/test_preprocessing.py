from ingestion import extract_text_from_pdf
from preprocessing import preprocess_pages


PDF_PATH = "../data/raw/2025_AnnualReport.pdf"


# Step 1: Extract
pages = extract_text_from_pdf(PDF_PATH)

# Step 2: Preprocess
processed_pages = preprocess_pages(pages)


print("=" * 60)
print("PREPROCESSING TEST")
print("=" * 60)

print(f"Original pages: {len(pages)}")
print(f"Processed pages: {len(processed_pages)}")
print(f"Removed empty pages: {len(pages) - len(processed_pages)}")


print("\nFirst processed page:")
print("-" * 60)
print(processed_pages[0])


print("\nFinancial statement page:")
print("-" * 60)

for page in processed_pages:
    if page["pdf_page"] == 36:
        print(page)
        break