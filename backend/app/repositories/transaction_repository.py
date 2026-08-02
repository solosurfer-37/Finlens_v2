from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transaction_schema import TransactionCreate


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: TransactionCreate) -> Transaction:
        transaction = Transaction(**data.model_dump())
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def bulk_create(self, transactions: list[TransactionCreate]) -> list[Transaction]:
        """
        Insert many transactions in a single DB round-trip.
        Used during CSV upload where hundreds/thousands of rows arrive at once.
        """
        objects = [Transaction(**t.model_dump()) for t in transactions]
        self.db.add_all(objects)
        self.db.commit()
        return objects

    def get_by_investigation(self, investigation_id: int) -> list[Transaction]:
        return self.db.query(Transaction).filter(
            Transaction.investigation_id == investigation_id
        ).all()