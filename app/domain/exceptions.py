class LedgerDomainError(Exception):
    """Base exception for domain-level ledger failures."""
    pass


class AccountNotFoundError(LedgerDomainError):
    """Raised when an account lookup fails."""
    pass


class InsufficientFundsError(LedgerDomainError):
    """Raised when a debit transaction exceeds the account balance."""
    pass