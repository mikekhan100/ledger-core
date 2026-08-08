from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import TransactionType

# --- Account Schemas ---

class AccountCreateRequest(BaseModel):
    owner_email: str = Field(..., description="Email address of account holder")
    currency: str = Field("GBP", min_length=3, max_length=3, description="ISO 4217 Currency Code")

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_email: str
    currency: str
    balance: Decimal
    created_at: datetime

# --- Transaction Schemas ---

class TransactionCreateRequest(BaseModel):
    account_id: UUID
    amount: Decimal = Field(..., gt=0, description="Transaction amount must be strictly positive")
    transaction_type: TransactionType
    reference: str = Field(..., min_length=3, max_length=100)

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    amount: Decimal
    transaction_type: TransactionType
    reference: str
    created_at: datetime