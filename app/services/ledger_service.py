from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import AccountNotFoundError, InsufficientFundsError
from app.domain.models import Account, Transaction, TransactionType
from app.domain.schemas import (
    AccountCreateRequest,
    TransactionCreateRequest,
)

logger = structlog.get_logger(__name__)


class LedgerService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session

    async def create_account(self, payload: AccountCreateRequest) -> Account:
        account = Account(
            owner_email=payload.owner_email,
            currency=payload.currency,
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)
        logger.info("account_created", account_id=str(account.id), email=account.owner_email)
        return account

    async def get_account(self, account_id: UUID) -> Account:
        stmt = select(Account).where(Account.id == account_id)
        result = await self.db.execute(stmt)
        account = result.scalar_one_or_none()
        if not account:
            raise AccountNotFoundError(f"Account with ID '{account_id}' not found.")
        return account

    async def record_transaction(self, payload: TransactionCreateRequest) -> Transaction:
        # Acquire row lock via with_for_update() to prevent balance race conditions
        stmt = select(Account).where(Account.id == payload.account_id).with_for_update()
        result = await self.db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            logger.warning("transaction_failed_no_account", account_id=str(payload.account_id))
            raise AccountNotFoundError(f"Account with ID '{payload.account_id}' not found.")

        if payload.transaction_type == TransactionType.DEBIT:
            if account.balance < payload.amount:
                logger.warning(
                    "insufficient_funds",
                    account_id=str(account.id),
                    balance=str(account.balance),
                    requested=str(payload.amount),
                )
                raise InsufficientFundsError("Insufficient balance for this debit transaction.")
            account.balance -= payload.amount
        else:
            account.balance += payload.amount

        transaction = Transaction(
            account_id=payload.account_id,
            amount=payload.amount,
            transaction_type=payload.transaction_type,
            reference=payload.reference,
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(
            "transaction_recorded",
            transaction_id=str(transaction.id),
            account_id=str(account.id),
            new_balance=str(account.balance),
        )
        return transaction