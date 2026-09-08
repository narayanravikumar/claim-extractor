def extract_text(pdf_bytes: bytes) -> str:
    """Return the text layer of a PDF."""
    raise NotImplementedError


def normalise_whitespace(text: str) -> str:
    """Collapse runs of whitespace into single spaces and strip the ends."""
    return " ".join(text.split())