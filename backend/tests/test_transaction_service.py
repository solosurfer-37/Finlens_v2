from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.investigation import Investigation
from app.models.transaction import Transaction
from app.models.user import User
from app.services.transaction_service import TransactionService


def make_investigation(db) -> int:
    user = User(email="svc@finlens.com", hashed_password="x")
    db.add(user)
    db.commit()
    inv = Investigation(user_id=user.id, filename="svc.csv")
    db.add(inv)
    db.commit()
    return inv.id


def make_row(ref: str, sender: str = "ACC-A", receiver: str = "ACC-B", amount: str = "100.00") -> dict:
    return {
        "transaction_reference": ref,
        "sender_account_number": sender,
        "sender_account_holder": f"Holder {sender}",
        "sender_bank_name": "BankX",
        "receiver_account_number": receiver,
        "receiver_account_holder": f"Holder {receiver}",
        "receiver_bank_name": "BankY",
        "amount": Decimal(amount),
        "currency": "INR",
        "transaction_time": datetime(2026, 1, 1, 10, 0, 0),
    }


def account_count(db) -> int:
    return db.query(Account).count()


def test_resolve_account_creates_new_account(db):
    service = TransactionService(db)
    account_id = service._resolve_account("ACC-NEW", "Alice", "BankX")

    assert db.get(Account, account_id).account_number == "ACC-NEW"
    assert account_count(db) == 1


def test_resolve_account_reuses_existing_account(db):
    service = TransactionService(db)
    first = service._resolve_account("ACC-1", "Alice", "BankX")
    second = service._resolve_account("ACC-1", "Alice", "BankX")

    assert first == second
    assert account_count(db) == 1


def test_process_rows_returns_count_and_saves_transactions(db):
    inv_id = make_investigation(db)
    rows = [make_row("T1"), make_row("T2", sender="ACC-C")]

    created = TransactionService(db).process_rows(inv_id, rows)

    assert created == 2
    assert db.query(Transaction).filter_by(investigation_id=inv_id).count() == 2


def test_process_rows_shares_accounts_across_rows(db):
    inv_id = make_investigation(db)
    rows = [make_row("T1"), make_row("T2"), make_row("T3")]

    TransactionService(db).process_rows(inv_id, rows)

    assert account_count(db) == 2


def test_process_rows_empty_list_returns_zero(db):
    inv_id = make_investigation(db)
    assert TransactionService(db).process_rows(inv_id, []) == 0


def test_duplicate_reference_in_same_investigation_is_rejected(db):
    inv_id = make_investigation(db)
    service = TransactionService(db)
    service.process_rows(inv_id, [make_row("T1")])

    with pytest.raises(IntegrityError):
        service.process_rows(inv_id, [make_row("T1")])

    db.rollback()
    assert db.query(Transaction).filter_by(investigation_id=inv_id).count() == 1


def test_same_reference_allowed_in_different_investigations(db):
    inv_a = make_investigation(db)
    inv_b_inv = Investigation(user_id=db.query(User).first().id, filename="b.csv")
    db.add(inv_b_inv)
    db.commit()

    service = TransactionService(db)
    service.process_rows(inv_a, [make_row("T1")])
    service.process_rows(inv_b_inv.id, [make_row("T1")])

    assert db.query(Transaction).count() == 2