from decimal import Decimal

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_health_check(client) -> None:
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_and_get_account_flow(client) -> None:
    create_res = await client.post(
        "/api/v1/accounts/",
        json={"owner_email": "api_user@example.com", "currency": "GBP"},
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    data = create_res.json()
    account_id = data["id"]
    assert data["owner_email"] == "api_user@example.com"
    assert Decimal(data["balance"]) == Decimal("0.00")

    get_res = await client.get(f"/api/v1/accounts/{account_id}")
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.json()["id"] == account_id


@pytest.mark.asyncio
async def test_transaction_api_flow(client) -> None:
    account_res = await client.post(
        "/api/v1/accounts/",
        json={"owner_email": "trader@example.com", "currency": "GBP"},
    )
    account_id = account_res.json()["id"]

    credit_res = await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": account_id,
            "amount": "200.00",
            "transaction_type": "CREDIT",
            "reference": "Initial deposit",
        },
    )
    assert credit_res.status_code == status.HTTP_201_CREATED

    debit_res = await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": account_id,
            "amount": "50.00",
            "transaction_type": "DEBIT",
            "reference": "Online order",
        },
    )
    assert debit_res.status_code == status.HTTP_201_CREATED

    acc_res = await client.get(f"/api/v1/accounts/{account_id}")
    assert Decimal(acc_res.json()["balance"]) == Decimal("150.00")


@pytest.mark.asyncio
async def test_overdraft_transaction_returns_400(client) -> None:
    account_res = await client.post(
        "/api/v1/accounts/",
        json={"owner_email": "poor@example.com", "currency": "GBP"},
    )
    account_id = account_res.json()["id"]

    debit_res = await client.post(
        "/api/v1/transactions/",
        json={
            "account_id": account_id,
            "amount": "100.00",
            "transaction_type": "DEBIT",
            "reference": "Overdraft test",
        },
    )
    assert debit_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Insufficient balance" in debit_res.json()["detail"]