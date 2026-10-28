from sqlalchemy.orm import Session

from app.models.account import Account
from app.schemas.account_schema import AccountCreate


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: AccountCreate, user_id: int) -> Account:
        account = Account(**data.model_dump(), user_id=user_id)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def get_by_id(self, account_id: int) -> Account | None:
        return self.db.get(Account, account_id)

    def get_by_account_number(self, user_id: int, account_number: str) -> Account | None:
        return self.db.query(Account).filter(
            Account.user_id == user_id,
            Account.account_number == account_number,
        ).first()

    def get_all(self) -> list[Account]:
        return self.db.query(Account).all()