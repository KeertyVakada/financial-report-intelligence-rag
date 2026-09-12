import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving useful line structure.
    """

    # Normalize different types of whitespace
    text = text.replace("\xa0", " ")

    # Remove trailing spaces from each line
    lines = [line.strip() for line in text.splitlines()]

    # Remove repeated blank lines
    cleaned_lines = []
    previous_blank = False

    for line in lines:
        if not line:
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False

    return "\n".join(cleaned_lines).strip()


def extract_report_page_number(text: str) -> int | None:
    """
    Try to identify the printed page number from the beginning
    of the extracted page text.

    Returns:
        Printed report page number if detected, otherwise None.
    """

    lines = text.splitlines()

    for line in lines[:3]:
        match = re.fullmatch(r"\d+", line.strip())

        if match:
            return int(match.group())

    return None


def preprocess_pages(pages: list[dict]) -> list[dict]:
    """
    Preprocess page-level PDF extraction results.

    Empty pages are removed.

    Each returned record contains:
        - chunk_source
        - pdf_page
        - report_page
        - text
        - character_count
    """

    processed_pages = []

    for page in pages:
        pdf_page = page["page_number"]

        cleaned_text = clean_text(page["text"])

        # Skip pages with no meaningful text
        if not cleaned_text:
            continue

        report_page = extract_report_page_number(cleaned_text)

        processed_pages.append(
            {
                "document": "Microsoft 2025 Annual Report",
                "pdf_page": pdf_page,
                "report_page": report_page,
                "text": cleaned_text,
                "character_count": len(cleaned_text),
            }
        )

    return processed_pages