from sqlalchemy.orm import Session

from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.account_schema import AccountCreate
from app.schemas.transaction_schema import TransactionCreate


class TransactionService:
    """
    Orchestrates account resolution + transaction creation
    from parsed CSV rows. Contains business logic —
    repositories only handle raw DB access.
    """

    def __init__(self, db: Session):
        self.account_repo = AccountRepository(db)
        self.transaction_repo = TransactionRepository(db)

    def _resolve_account(self, account_number: str, holder: str, bank: str) -> int:
        """Returns existing account's ID, or creates a new one."""
        account = self.account_repo.get_by_account_number(account_number)
        if account:
            return account.id

        new_account = self.account_repo.create(
            AccountCreate(
                account_number=account_number,
                account_holder=holder,
                bank_name=bank,
            )
        )
        return new_account.id

    def process_rows(self, investigation_id: int, rows: list[dict]) -> int:
        """
        Takes parsed CSV rows, resolves accounts, and bulk-creates transactions.
        Returns the count of transactions created.
        """
        transactions_to_create = []

        for row in rows:
            sender_id = self._resolve_account(
                row["sender_account_number"],
                row["sender_account_holder"],
                row["sender_bank_name"],
            )
            receiver_id = self._resolve_account(
                row["receiver_account_number"],
                row["receiver_account_holder"],
                row["receiver_bank_name"],
            )

            transactions_to_create.append(
                TransactionCreate(
                    transaction_reference=row["transaction_reference"],
                    investigation_id=investigation_id,
                    sender_account_id=sender_id,
                    receiver_account_id=receiver_id,
                    amount=row["amount"],
                    currency=row["currency"],
                    transaction_time=row["transaction_time"],
                )
            )

        created = self.transaction_repo.bulk_create(transactions_to_create)
        return len(created)