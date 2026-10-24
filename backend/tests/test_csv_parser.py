from datetime import datetime
from decimal import Decimal

import pytest

from app.services.csv_parser import CSVParseError, parse_transaction_csv

HEADER = (
    "transaction_reference,sender_account_number,sender_account_holder,"
    "sender_bank_name,receiver_account_number,receiver_account_holder,"
    "receiver_bank_name,amount,currency,transaction_time"
)


def write_csv(tmp_path, rows, header=HEADER):
    path = tmp_path / "t.csv"
    path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return str(path)


def row(amount="1000", ref="TX-1"):
    return f"{ref},ACC-A,Alice,BankX,ACC-B,Bob,BankY,{amount},INR,2026-01-01 10:00:00"


def test_valid_row_parsed_with_decimal_amount(tmp_path):
    rows = parse_transaction_csv(write_csv(tmp_path, [row("1234567.89")]))
    assert len(rows) == 1
    assert isinstance(rows[0]["amount"], Decimal)
    assert rows[0]["amount"] == Decimal("1234567.89")
    assert rows[0]["transaction_reference"] == "TX-1"
    assert rows[0]["transaction_time"] == datetime(2026, 1, 1, 10, 0, 0)


def test_missing_column_raises(tmp_path):
    bad_header = HEADER.replace("currency,", "")
    path = write_csv(tmp_path, ["TX-1,A,B,C,D,E,F,100,2026-01-01 10:00:00"], bad_header)
    with pytest.raises(CSVParseError):
        parse_transaction_csv(path)


def test_invalid_amount_raises(tmp_path):
    with pytest.raises(CSVParseError):
        parse_transaction_csv(write_csv(tmp_path, [row("abc")]))


@pytest.mark.parametrize("amount", ["0", "-50"])
def test_non_positive_amount_raises(tmp_path, amount):
    with pytest.raises(CSVParseError):
        parse_transaction_csv(write_csv(tmp_path, [row(amount)]))


def test_empty_amount_raises_parse_error(tmp_path):
    with pytest.raises(CSVParseError):
        parse_transaction_csv(write_csv(tmp_path, [row("")]))