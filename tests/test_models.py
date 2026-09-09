import pytest
from datetime import date
from decimal import Decimal
from pydantic import ValidationError

from claim_extractor.models.claim import ClaimDocument

def test_valid_claim_is_created():
    claim = ClaimDocument(claimant_name="John Smith", date_of_loss=date(2024, 3, 12))
    assert claim.claimant_name == "John Smith"

def test_future_date_rejected():
    with pytest.raises(ValidationError):
        ClaimDocument(claimant_name="John Smith", date_of_loss=date(2099, 1, 1))

def test_negative_amount():
    with pytest.raises(ValidationError):
        ClaimDocument(claimant_name="John Smith", date_of_loss=date(2099, 1, 1), amount_claimed=Decimal(-500))