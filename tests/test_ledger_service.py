from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.exceptions import AccountNotFoundError, InsufficientFundsError
from app.domain.schemas import (
    AccountCreateRequest,
    TransactionCreateRequest,
    TransactionType,
)
from app.services.ledger_service import LedgerService


@pytest.mark.asyncio
async def test_create_account(db_session) -> None:
    service = LedgerService(db_session)
    payload = AccountCreateRequest(owner_email="user@example.com", currency="GBP")

    account = await service.create_account(payload)

    assert account.id is not None
    assert account.owner_email == "user@example.com"
    assert account.balance == Decimal("0.00")
    assert account.currency == "GBP"


@pytest.mark.asyncio
async def test_credit_transaction_updates_balance(db_session) -> None:
    service = LedgerService(db_session)
    account = await service.create_account(
        AccountCreateRequest(owner_email="user@example.com", currency="GBP")
    )

    tx_request = TransactionCreateRequest(
        account_id=account.id,
        amount=Decimal("150.50"),
        transaction_type=TransactionType.CREDIT,
        reference="Salary deposit",
    )
    transaction = await service.record_transaction(tx_request)

    updated_account = await service.get_account(account.id)
    assert transaction.amount == Decimal("150.50")
    assert updated_account.balance == Decimal("150.50")


@pytest.mark.asyncio
async def test_debit_transaction_success(db_session) -> None:
    service = LedgerService(db_session)
    account = await service.create_account(
        AccountCreateRequest(owner_email="user@example.com", currency="GBP")
    )

    await service.record_transaction(
        TransactionCreateRequest(
            account_id=account.id,
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            reference="Initial fund",
        )
    )

    await service.record_transaction(
        TransactionCreateRequest(
            account_id=account.id,
            amount=Decimal("40.00"),
            transaction_type=TransactionType.DEBIT,
            reference="Grocery shopping",
        )
    )

    updated_account = await service.get_account(account.id)
    assert updated_account.balance == Decimal("60.00")


@pytest.mark.asyncio
async def test_debit_insufficient_funds_raises_error(db_session) -> None:
    service = LedgerService(db_session)
    account = await service.create_account(
        AccountCreateRequest(owner_email="user@example.com", currency="GBP")
    )

    tx_request = TransactionCreateRequest(
        account_id=account.id,
        amount=Decimal("50.00"),
        transaction_type=TransactionType.DEBIT,
        reference="ATM withdrawal",
    )

    with pytest.raises(InsufficientFundsError):
        await service.record_transaction(tx_request)


@pytest.mark.asyncio
async def test_transaction_nonexistent_account_raises_error(db_session) -> None:
    service = LedgerService(db_session)
    random_id = uuid4()

    tx_request = TransactionCreateRequest(
        account_id=random_id,
        amount=Decimal("10.00"),
        transaction_type=TransactionType.CREDIT,
        reference="Ghost account test",
    )

    with pytest.raises(AccountNotFoundError):
        await service.record_transaction(tx_request)