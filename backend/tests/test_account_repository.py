from app.models.account import Account
from app.models.user import User
from app.repositories.account_repository import AccountRepository


def make_user(db, email="repo@finlens.com"):
    user = User(email=email, hashed_password="not-a-real-hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_accounts(db, user_id, count):
    accounts = [
        Account(
            user_id=user_id,
            account_number=f"ACC-{i}",
            account_holder=f"Holder {i}",
            bank_name="BankX",
        )
        for i in range(1, count + 1)
    ]
    db.add_all(accounts)
    db.commit()
    return accounts


def test_get_by_ids_returns_dict_keyed_by_id(db):
    user = make_user(db)
    accounts = make_accounts(db, user.id, 3)
    wanted = {accounts[0].id, accounts[2].id}

    result = AccountRepository(db).get_by_ids(wanted)

    assert set(result.keys()) == wanted
    assert result[accounts[0].id].account_number == "ACC-1"
    assert result[accounts[2].id].account_number == "ACC-3"


def test_get_by_ids_empty_returns_empty_dict(db):
    assert AccountRepository(db).get_by_ids([]) == {}
    assert AccountRepository(db).get_by_ids(set()) == {}


def test_get_by_ids_ignores_missing_ids(db):
    user = make_user(db)
    accounts = make_accounts(db, user.id, 1)

    result = AccountRepository(db).get_by_ids([accounts[0].id, 99999])

    assert list(result.keys()) == [accounts[0].id]