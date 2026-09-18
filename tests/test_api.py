from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

from claim_extractor.exceptions import LLMExtractionError
from claim_extractor.main import app
from claim_extractor.models.claim import ClaimDocument

client = TestClient(app)


def test_rejects_non_pdf_with_400():
    response = client.post(
        "/extract",
        files={"file": ("claim.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 400


def test_pdf_with_no_text_returns_422():
    with patch("claim_extractor.api.routes.extract_text", return_value=""):
        response = client.post(
            "/extract",
            files={"file": ("claim.pdf", b"%PDF-1.4 scanned image only", "application/pdf")},
        )
    assert response.status_code == 422


def test_valid_pdf_returns_claim_document():
    parsed = ClaimDocument(claimant_name="Jane Doe", date_of_loss=date(2024, 5, 1))
    with (
        patch("claim_extractor.api.routes.extract_text", return_value="Claimant: Jane Doe"),
        patch("claim_extractor.api.routes.parse_claim_fields", return_value=parsed),
    ):
        response = client.post(
            "/extract",
            files={"file": ("claim.pdf", b"%PDF-1.4 fake body", "application/pdf")},
        )
    assert response.status_code == 200
    assert response.json()["claimant_name"] == "Jane Doe"


def test_unparseable_llm_reply_returns_502():
    with (
        patch("claim_extractor.api.routes.extract_text", return_value="Claimant: Jane Doe"),
        patch(
            "claim_extractor.api.routes.parse_claim_fields",
            side_effect=LLMExtractionError("Model reply was not valid JSON"),
        ),
    ):
        response = client.post(
            "/extract",
            files={"file": ("claim.pdf", b"%PDF-1.4 fake body", "application/pdf")},
        )
    assert response.status_code == 502
