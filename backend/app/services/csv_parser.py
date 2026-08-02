from decimal import Decimal , InvalidOperation
import pandas as pd 
REQUIRED_COLUMNS = {
    "transaction_reference" ,
    "sender_account_number",
    "sender_account_holder" , 
    "sender_bank_name" , 
    "receiver_account_number",
    "receiver_account_holder" , 
    "receiver_bank_name" , 
    "amount" , 
    "currency" ,
    "transaction time " , 

}


class CSVParseError(Exception) :
    """Raised when the uploaded CSV is invalid or malformed."""

def parse_transaction_csv(file_path:str) -> list[dict]:
    """
    Reads the Bank transaction CSV and returns a list of clean row dicts.
    Raises CSVParseError if required columns are missing .
    """

    df = pd.read_csv(file.path)

    missing = REQUIRED_COLUMNS - set(df.columns) 
    if missing :
        raise CSVParseError(f"Missing required columns : {missing}")

    rows = []
    for _, row in df.iterrows():
        try:
            amount = Decimal(str(row["amount"])) 
        except InvalidOperation :
            raise CSVParserError(f"Invalid amount value :{row['amount']}")

        if amount <= 0 :
            raise CSVParseError(f"Amount must be positive :{amount}") 

        rows.append({
            "transaction_reference" : str(row["transaction_reference"]) ,
            "sender_account_number": str(row["sender_account_number"]),
            "sender_account_holder" :str(row["sender_account_holder"]),
            "sender_bank_name" : str(row["sender_bank_name"]) ,
            "receiver_account_number": str(row["receiver_account_number"]),
            "receiver_account_holder" :str(row["receiver_account_holder"]),
            "receiver_bank_name" : str(row["receiver_bank_name"]) ,
            "amount " : amount ,
            "currency " : str(row["currency "]) , 
            "transaction_time" : pd.to_datetime(row["transaction_time"])
        })

        return rows 