import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class TransactionType(StrEnum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GBP")
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2), 
        default=Decimal("0.00"), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC)
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account", 
        cascade="all, delete-orphan"
    )

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id"), 
        nullable=False, 
        index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType), 
        nullable=False
    )
    reference: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC)
    )

    account: Mapped[Account] = relationship(back_populates="transactions")