from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.investigation import Investigation
from app.models.transaction import Transaction
from app.models.user import User
from app.services.transaction_service import TransactionService


def make_user(db, email: str = "svc@finlens.com") -> int:
    user = User(email=email, hashed_password="x")
    db.add(user)
    db.commit()
    return user.id


def make_investigation(db, user_id: int, filename: str = "svc.csv") -> int:
    inv = Investigation(user_id=user_id, filename=filename)
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
    user_id = make_user(db)
    service = TransactionService(db, user_id)
    account_id = service._resolve_account("ACC-NEW", "Alice", "BankX")

    account = db.get(Account, account_id)
    assert account.account_number == "ACC-NEW"
    assert account.user_id == user_id
    assert account_count(db) == 1


def test_resolve_account_reuses_existing_account(db):
    user_id = make_user(db)
    service = TransactionService(db, user_id)
    first = service._resolve_account("ACC-1", "Alice", "BankX")
    second = service._resolve_account("ACC-1", "Alice", "BankX")

    assert first == second
    assert account_count(db) == 1


def test_same_account_number_for_two_users_gives_separate_accounts(db):
    user_a = make_user(db, "a@finlens.com")
    user_b = make_user(db, "b@finlens.com")

    id_a = TransactionService(db, user_a)._resolve_account("ACC-SHARED", "Alice", "BankX")
    id_b = TransactionService(db, user_b)._resolve_account("ACC-SHARED", "Mallory", "BankZ")

    assert id_a != id_b
    assert db.get(Account, id_a).account_holder == "Alice"
    assert db.get(Account, id_b).account_holder == "Mallory"
    assert account_count(db) == 2


def test_user_never_gets_other_users_account(db):
    user_a = make_user(db, "a@finlens.com")
    user_b = make_user(db, "b@finlens.com")
    id_a = TransactionService(db, user_a)._resolve_account("ACC-1", "Alice", "BankX")

    id_b = TransactionService(db, user_b)._resolve_account("ACC-1", "Bob", "BankY")

    assert db.get(Account, id_b).user_id == user_b
    assert id_b != id_a


def test_duplicate_account_number_within_same_user_is_rejected(db):
    user_id = make_user(db)
    db.add(Account(user_id=user_id, account_number="ACC-1", account_holder="A", bank_name="B"))
    db.commit()
    db.add(Account(user_id=user_id, account_number="ACC-1", account_holder="C", bank_name="D"))

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_process_rows_returns_count_and_saves_transactions(db):
    user_id = make_user(db)
    inv_id = make_investigation(db, user_id)
    rows = [make_row("T1"), make_row("T2", sender="ACC-C")]

    created = TransactionService(db, user_id).process_rows(inv_id, rows)

    assert created == 2
    assert db.query(Transaction).filter_by(investigation_id=inv_id).count() == 2


def test_process_rows_shares_accounts_across_rows(db):
    user_id = make_user(db)
    inv_id = make_investigation(db, user_id)
    rows = [make_row("T1"), make_row("T2"), make_row("T3")]

    TransactionService(db, user_id).process_rows(inv_id, rows)

    assert account_count(db) == 2


def test_process_rows_empty_list_returns_zero(db):
    user_id = make_user(db)
    inv_id = make_investigation(db, user_id)
    assert TransactionService(db, user_id).process_rows(inv_id, []) == 0


def test_duplicate_reference_in_same_investigation_is_rejected(db):
    user_id = make_user(db)
    inv_id = make_investigation(db, user_id)
    service = TransactionService(db, user_id)
    service.process_rows(inv_id, [make_row("T1")])

    with pytest.raises(IntegrityError):
        service.process_rows(inv_id, [make_row("T1")])

    db.rollback()
    assert db.query(Transaction).filter_by(investigation_id=inv_id).count() == 1


def test_same_reference_allowed_in_different_investigations(db):
    user_id = make_user(db)
    inv_a = make_investigation(db, user_id, "a.csv")
    inv_b = make_investigation(db, user_id, "b.csv")

    service = TransactionService(db, user_id)
    service.process_rows(inv_a, [make_row("T1")])
    service.process_rows(inv_b, [make_row("T1")])

    assert db.query(Transaction).count() == 2