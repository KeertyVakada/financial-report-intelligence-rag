from ingestion import extract_text_from_pdf


PDF_PATH = "../data/raw/2025_AnnualReport.pdf"


pages = extract_text_from_pdf(PDF_PATH)

print(f"Number of pages extracted: {len(pages)}")

print("\n--- First page ---")
print(pages[0]["text"][:1000])

print("\n--- Page 36 ---")
print(pages[35]["text"][:1500])