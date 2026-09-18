from fastapi import APIRouter, File, HTTPException, UploadFile

from claim_extractor.exceptions import InvalidPDFError, LLMExtractionError
from claim_extractor.extraction.base import extract_text, parse_claim_fields, validate_pdf
from claim_extractor.models.claim import ClaimDocument

router = APIRouter()


@router.post("/extract", response_model=ClaimDocument)
async def extract_claim(file: UploadFile = File(...)) -> ClaimDocument:
    """Extract structured claim data from an uploaded PDF."""
    pdf_bytes = await file.read()

    try:
        validate_pdf(pdf_bytes)
    except InvalidPDFError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    text = extract_text(pdf_bytes)
    if not text:
        raise HTTPException(
            status_code=422,
            detail="PDF has no readable text layer.",
        )

    try:
        return parse_claim_fields(text)
    except LLMExtractionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
