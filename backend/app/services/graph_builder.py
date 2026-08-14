from app.engine.fraud_signal import FraudSignal
from app.models.account import Account
from app.models.transaction import Transaction

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


class GraphBuilder:
    """
    Converts transactions + fraud signals into a node/edge graph structure
    ready for frontend visualization (vis-network format).
    """

    def build(
        self,
        transactions: list[Transaction],
        accounts: dict[int, Account],
        signals: list[FraudSignal],
    ) -> dict:
        flagged_accounts = self._collect_flagged_accounts(signals)
        flagged_transactions = self._collect_flagged_transactions(signals)

        nodes = self._build_nodes(transactions, accounts, flagged_accounts)
        edges = self._build_edges(transactions, flagged_transactions)

        return {"nodes": nodes, "edges": edges}

    def _collect_flagged_accounts(self, signals: list[FraudSignal]) -> dict[int, str]:
        """Maps account_id -> highest severity it was flagged with."""
        flagged = {}
        for signal in signals:
            for account_id in signal.related_account_ids:
                current = flagged.get(account_id)
                if current is None or SEVERITY_RANK[signal.severity] > SEVERITY_RANK[current]:
                    flagged[account_id] = signal.severity
        return flagged

    def _collect_flagged_transactions(self, signals: list[FraudSignal]) -> dict[int, str]:
        """Maps transaction_id -> highest severity it was flagged with."""
        flagged = {}
        for signal in signals:
            for txn_id in signal.related_transaction_ids:
                current = flagged.get(txn_id)
                if current is None or SEVERITY_RANK[signal.severity] > SEVERITY_RANK[current]:
                    flagged[txn_id] = signal.severity
        return flagged

    def _build_nodes(
        self,
        transactions: list[Transaction],
        accounts: dict[int, Account],
        flagged_accounts: dict[int, str],
    ) -> list[dict]:
        account_ids = set()
        for txn in transactions:
            account_ids.add(txn.sender_account_id)
            account_ids.add(txn.receiver_account_id)

        nodes = []
        for account_id in account_ids:
            account = accounts.get(account_id)
            nodes.append({
                "id": account_id,
                "label": account.account_number if account else str(account_id),
                "flagged": account_id in flagged_accounts,
                "severity": flagged_accounts.get(account_id),
            })
        return nodes

    def _build_edges(
        self,
        transactions: list[Transaction],
        flagged_transactions: dict[int, str],
    ) -> list[dict]:
        edges = []
        for txn in transactions:
            edges.append({
                "id": txn.id,
                "from": txn.sender_account_id,
                "to": txn.receiver_account_id,
                "amount": str(txn.amount),
                "flagged": txn.id in flagged_transactions,
                "severity": flagged_transactions.get(txn.id),
            })
        return edges