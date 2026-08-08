from typing import Annotated

from app.domain.exceptions import AccountNotFoundError, InsufficientFundsError
from app.services.ledger_service import LedgerService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.domain.schemas import TransactionCreateRequest, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreateRequest,
    db: DbSession,
) -> TransactionResponse:
    service = LedgerService(db)
    try:
        transaction = await service.record_transaction(payload)
        return TransactionResponse.model_validate(transaction)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InsufficientFundsError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc