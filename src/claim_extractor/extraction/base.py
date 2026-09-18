import io
import json
import os

import pdfplumber
from anthropic import Anthropic
from pydantic import ValidationError

from claim_extractor.exceptions import InvalidPDFError, LLMExtractionError
from claim_extractor.models.claim import ClaimDocument


def extract_text(pdf_bytes: bytes) -> str:
    """Return the text layer of a PDF."""
    parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                parts.append(page_text)
    return "\n".join(parts).strip()


def normalise_whitespace(text: str) -> str:
    """Collapse runs of whitespace into single spaces and strip the ends."""
    return " ".join(text.split())


def validate_pdf(pdf_bytes: bytes) -> None:
    """Raise InvalidPDFError if the bytes are not in a pdf"""
    if not pdf_bytes.startswith(b"%PDF-"):
        raise InvalidPDFError("File is not a pdf.")


# Model choice, JSON-failure handling and "good enough" accuracy are all
# covered by ADR 003. Do not change the model or the failure behaviour
# below without updating that record.
_MODEL = os.environ.get("CLAIM_EXTRACTOR_MODEL", "claude-3-5-haiku-latest")

_EXTRACTION_PROMPT = """Extract claim fields from the text below and reply
with a single JSON object only, no prose, matching this shape:

{{"claimant_name": str, "date_of_loss": "YYYY-MM-DD", "policy_number": str or null,
"claim_type": str or null, "amount_claimed": number or null}}

If a field is not present in the text, use null. Do not guess a date or
amount that is not stated.

TEXT:
{text}
"""


def parse_claim_fields(text: str) -> ClaimDocument:
    """Turn extracted claim text into a ClaimDocument via an LLM call.

    Raises LLMExtractionError if the model's reply is not valid JSON, or is
    valid JSON that does not satisfy ClaimDocument (see ADR 003 for why
    this fails closed instead of returning a partial or guessed record).
    """
    client = Anthropic()
    response = client.messages.create(
        model=_MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": _EXTRACTION_PROMPT.format(text=text)}],
    )
    raw = response.content[0].text

    try:
        fields = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LLMExtractionError(
            f"Model reply was not valid JSON: {exc}"
        ) from exc

    try:
        return ClaimDocument(**fields)
    except ValidationError as exc:
        raise LLMExtractionError(
            f"Model reply did not match the claim schema: {exc}"
        ) from exc
