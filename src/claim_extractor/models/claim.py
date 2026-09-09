from pydantic import BaseModel, field_validator
from datetime import date
from decimal import Decimal

class ClaimDocument(BaseModel):
    claimant_name: str
    date_of_loss: date
    policy_number: str | None = None
    claim_type: str | None = None
    amount_claimed: Decimal | None = None

    @field_validator("date_of_loss")
    @classmethod
    def check_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("date of loss cannot be in the future")
        return v

    @field_validator("amount_claimed")
    @classmethod
    def check_not_negative(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v < 0:
            raise ValueError("amount claimed cannot be negative")
        return v