def _get_overlap_units(
    units: list[str],
    overlap_chars: int,
) -> list[str]:
    """
    Get complete units from the end of a chunk to use as overlap.
    """

    overlap_units = []
    total_length = 0

    for unit in reversed(units):
        unit_length = len(unit)

        if total_length + unit_length > overlap_chars:
            break

        overlap_units.insert(0, unit)
        total_length += unit_length

    return overlap_units


def split_text_into_chunks(
    text: str,
    max_chars: int = 1200,
    overlap_chars: int = 200,
    min_chars: int = 200,
) -> list[str]:
    """
    Split text into meaningful, overlapping chunks.

    The function:
    - preserves paragraph/line boundaries where possible
    - keeps chunks below max_chars
    - uses complete units for overlap
    - avoids tiny standalone chunks
    """

    if not text.strip():
        return []

    if overlap_chars >= max_chars:
        raise ValueError(
            "overlap_chars must be smaller than max_chars."
        )

    # Prefer paragraph boundaries.
    units = [
        block.strip()
        for block in text.split("\n\n")
        if block.strip()
    ]

    # If the page has poor paragraph structure,
    # fall back to non-empty lines.
    if len(units) == 1 and len(units[0]) > max_chars:
        units = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    # Handle extremely large individual units.
    expanded_units = []

    for unit in units:
        if len(unit) <= max_chars:
            expanded_units.append(unit)
            continue

        start = 0

        while start < len(unit):
            end = start + max_chars
            piece = unit[start:end].strip()

            if piece:
                expanded_units.append(piece)

            start = end - overlap_chars

    units = expanded_units

    chunks = []
    current_units = []
    current_length = 0

    for unit in units:

        unit_length = len(unit)

        # Start a new chunk if adding this unit would exceed the limit.
        if current_units:
            proposed_length = (
                current_length + 2 + unit_length
            )

            if proposed_length > max_chars:

                chunk = "\n\n".join(current_units)
                chunks.append(chunk)

                # Build overlap using complete units.
                overlap_units = _get_overlap_units(
                    current_units,
                    overlap_chars,
                )

                overlap_length = sum(
                    len(item) for item in overlap_units
                )

                # Only keep overlap if the new unit still fits.
                if (
                    overlap_units
                    and overlap_length + 2 + unit_length <= max_chars
                ):
                    current_units = overlap_units + [unit]
                    current_length = (
                        overlap_length + 2 + unit_length
                    )
                else:
                    current_units = [unit]
                    current_length = unit_length

                continue

        current_units.append(unit)
        current_length = (
            unit_length
            if len(current_units) == 1
            else current_length + 2 + unit_length
        )

    if current_units:
        chunks.append("\n\n".join(current_units))

    # ---------------------------------------------------------
    # Merge tiny chunks with neighboring chunks.
    # ---------------------------------------------------------

    merged_chunks = []

    for chunk in chunks:

        if not merged_chunks:
            merged_chunks.append(chunk)
            continue

        # If the current chunk is too small, merge it backward
        # when possible.
        if len(chunk) < min_chars:

            previous = merged_chunks[-1]

            combined = previous + "\n\n" + chunk

            if len(combined) <= max_chars:
                merged_chunks[-1] = combined
            else:
                merged_chunks.append(chunk)

        else:
            merged_chunks.append(chunk)

    # If the first chunk is tiny, merge it forward.
    if (
        len(merged_chunks) > 1
        and len(merged_chunks[0]) < min_chars
    ):
        combined = (
            merged_chunks[0]
            + "\n\n"
            + merged_chunks[1]
        )

        if len(combined) <= max_chars:
            merged_chunks = [
                combined
            ] + merged_chunks[2:]

    return merged_chunks


def create_chunks(
    processed_pages: list[dict],
    max_chars: int = 1200,
    overlap_chars: int = 200,
    min_chars: int = 200,
) -> list[dict]:
    """
    Create page-aware chunks from preprocessed pages.

    Every chunk retains:
    - document
    - PDF page
    - printed report page
    - unique chunk ID
    """

    chunks = []

    for page in processed_pages:

        page_chunks = split_text_into_chunks(
            text=page["text"],
            max_chars=max_chars,
            overlap_chars=overlap_chars,
            min_chars=min_chars,
        )

        for chunk_number, chunk_text in enumerate(
            page_chunks,
            start=1,
        ):

            chunks.append(
                {
                    "chunk_id": (
                        f"msft_2025_"
                        f"pdf{page['pdf_page']}_"
                        f"chunk{chunk_number}"
                    ),
                    "document": page["document"],
                    "pdf_page": page["pdf_page"],
                    "report_page": page["report_page"],
                    "text": chunk_text,
                    "character_count": len(chunk_text),
                }
            )

    return chunks