# Ledger Core Service

A production-ready Python backend engine for financial account ledger tracking, built with **FastAPI**, **Async SQLAlchemy 2.0**, **Pydantic v2**, and **PostgreSQL** (with local SQLite support).

---

## Architecture & Project Structure

```text
ledger-core/
├── .github/
│   └── workflows/
│       └── ci.yml             # CI Quality Gate (Ruff, Mypy, Pytest)
├── app/
│   ├── api/
│   │   ├── dependencies.py    # Database session dependencies
│   │   └── v1/
│   │       ├── accounts.py    # Account REST endpoints
│   │       └── transactions.py# Transaction REST endpoints
│   ├── core/
│   │   ├── config.py          # App settings via pydantic-settings
│   │   └── database.py        # Async SQLAlchemy engine & session factory
│   ├── domain/
│   │   ├── exceptions.py      # Domain-specific error types
│   │   ├── models.py          # SQLAlchemy 2.0 ORM entities
│   │   └── schemas.py         # Pydantic v2 validation contracts
│   ├── services/
│   │   └── ledger_service.py  # Core business & balance processing engine
│   └── main.py                # FastAPI entrypoint & lifespan lifecycle
├── tests/
│   ├── conftest.py            # Async test client & in-memory DB fixtures
│   ├── test_api.py            # Integration tests for HTTP contracts
│   └── test_ledger_service.py # Unit tests for service logic & invariants
├── pyproject.toml             # Dependency specification & tool configs
├── uv.lock                    # Deterministic lockfile
└── README.md
```

## Local Setup & Quickstart

This project uses uv for fast, deterministic dependency management.

1. Installation

```text
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/ledger-core.git](https://github.com/YOUR_USERNAME/ledger-core.git)
cd ledger-core

# Synchronize dependencies with locked versions
uv sync --extra dev
```

2. Run Local Server

```text
uv run uvicorn app.main:app --reload
```

Interactive OpenAPI Docs: http://127.0.0.1:8000/docs

Health Check: http://127.0.0.1:8000/health

3. Run Quality Gates

```text
# Linter checks
uv run ruff check .

# Type checking
uv run mypy app

# Test suite
uv run pytest -v
```

## Maintainability Decisions

1. Naming choices
Layered Nomenclature: The codebase enforces strict separation between ORM database entities (app/domain/models.py), public API contract models (app/domain/schemas.py), and domain operational services (app/services/).

Explicit Financial Terms: Model and field names mirror financial domain entities (Account, Transaction, credit, debit, balance) rather than generic CRUD abstractions (Item, User, Data).

Request/Response Suffixes: DTO schemas explicitly use suffixes like AccountCreateRequest and TransactionResponse to prevent ambiguity between wire-format API payloads and internal database entities.

2. Where Type Hints Matter
Service Boundaries: All LedgerService methods mandate strict argument types and return signatures. This allows static type analysis to catch breaking schema or contract changes prior to execution.

ORM Mapped Attributes: Utilising SQLAlchemy 2.0's Mapped[...] generics bridges the gap between database columns and Python types, enabling automatic typing when building queries.

Financial Calculations: Monetary amounts are explicitly typed as Decimal (never floating-point float) across Pydantic schemas, ORM models and service computations to avoid rounding loss.

3. How Dependencies Are Managed
Lockfile Enforcement: We use uv with uv.lock to guarantee deterministic builds across local development, CI pipelines, and production container environments.

Isolated Dev Tooling: Tooling dependencies (pytest, mypy, ruff) are isolated under [project.optional-dependencies] inside pyproject.toml to keep production runtime environments minimal and secure.

4. How Upgrades Are Handled
Version Pins: Dependencies in pyproject.toml use compatible version bounds (>=X.Y.Z) to allow non-breaking security patches while preventing accidental breaking API changes.

Automated CI Lock Checks: CI executes uv sync --frozen to confirm that direct dependencies in pyproject.toml match uv.lock. Upgrades are isolated to deliberate PRs using uv lock --upgrade-package <package>.

5. What the Tests Protect
Invariant Protection: Unit tests explicitly protect business invariants — verifying that debits cannot drop account balances below 0.00 and ensuring row locking (with_for_update()) guards against race conditions.

API Schema Contracts: Integration tests verify HTTP status code translations (201 Created, 400 Bad Request, 404 Not Found) and ensure payload field serialisation matches public OpenAPI specifications.

6. What Could be Improved Next
Redis Idempotency Keys: Introduce an Idempotency-Key header check backed by Redis to safely handle network retries without creating duplicate monetary transactions.

Outbox Pattern for Async Events: Implement a transactional Outbox table pattern in PostgreSQL to reliably publish transaction lifecycle events to Apache Kafka or RabbitMQ.

Database Migrations Pipeline: Integrate Alembic migration scripts and run automated schema upgrades inside CI testing pipelines.

