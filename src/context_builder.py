from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))


# -------------------------------------------------------------------
# Context Builder
# -------------------------------------------------------------------

def build_context(
    retrieved_chunks: list[dict],
    max_chunks: int = 5,
) -> str:
    """
    Build a structured context string from retrieved financial evidence.

    Each evidence block contains:
    - Source
    - PDF page
    - Report page
    - Evidence type
    - Chunk ID
    - Retrieved text
    """

    if not retrieved_chunks:
        return ""

    selected_chunks = retrieved_chunks[:max_chunks]

    context_blocks = []

    for index, chunk in enumerate(
        selected_chunks,
        start=1,
    ):

        source = chunk.get(
            "document",
            "Unknown document",
        )

        pdf_page = chunk.get(
            "pdf_page",
            "Unknown",
        )

        report_page = chunk.get(
            "report_page",
            "Unknown",
        )

        evidence_type = chunk.get(
            "evidence_type",
            "general",
        )

        chunk_id = chunk.get(
            "chunk_id",
            "Unknown",
        )

        text = chunk.get(
            "text",
            "",
        ).strip()

        block = (
            f"[Evidence {index}]\n"
            f"Source: {source}\n"
            f"PDF page: {pdf_page}\n"
            f"Report page: {report_page}\n"
            f"Evidence type: {evidence_type}\n"
            f"Chunk ID: {chunk_id}\n"
            f"Text:\n{text}"
        )

        context_blocks.append(block)

    return "\n\n" + ("\n\n" + "-" * 80 + "\n\n").join(
        context_blocks
    )