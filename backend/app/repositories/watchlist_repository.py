from sqlalchemy.orm import Session

from app.models.watchlist import WatchlistEntry


class WatchlistRepository:
    def __init__(self, db: Session):
        self.db = db

    def is_account_flagged(self, account_number: str) -> bool:
        entry = self.db.query(WatchlistEntry).filter(
            WatchlistEntry.account_number == account_number
        ).first()
        return entry is not None

    def get_all_flagged_numbers(self) -> set[str]:
        entries = self.db.query(WatchlistEntry).all()
        return {e.account_number for e in entries}