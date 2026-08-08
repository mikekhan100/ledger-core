from typing import Annotated
from uuid import UUID

from app.domain.exceptions import AccountNotFoundError
from app.services.ledger_service import LedgerService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.domain.schemas import AccountCreateRequest, AccountResponse

router = APIRouter(prefix="/accounts", tags=["Accounts"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreateRequest,
    db: DbSession,
) -> AccountResponse:
    service = LedgerService(db)
    account = await service.create_account(payload)
    return AccountResponse.model_validate(account)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    db: DbSession,
) -> AccountResponse:
    service = LedgerService(db)
    try:
        account = await service.get_account(account_id)
        return AccountResponse.model_validate(account)
    except AccountNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc