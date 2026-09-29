from sqlalchemy.orm import Session

from app.core.cache import get_cache, set_cache
from app.engine.fraud_signal import FraudSignal
from app.repositories.account_repository import AccountRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.graph_builder import GraphBuilder


class GraphController:
    """
    Builds the transaction graph for a given investigation,
    using already-computed Evidence rather than re-running detection.
    Results are cached in Redis to avoid recomputation on repeated requests.
    """

    def __init__(self, db: Session):
        self.transaction_repo = TransactionRepository(db)
        self.account_repo = AccountRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.graph_builder = GraphBuilder()

    def get_graph(self, investigation_id: int) -> dict:
        cache_key = f"graph:{investigation_id}"
        cached = get_cache(cache_key)
        if cached is not None:
            return cached

        transactions = self.transaction_repo.get_by_investigation(investigation_id)

        account_ids = set()
        for txn in transactions:
            account_ids.add(txn.sender_account_id)
            account_ids.add(txn.receiver_account_id)

        accounts = {
            account_id: self.account_repo.get_by_id(account_id)
            for account_id in account_ids
        }

        evidence_list = self.evidence_repo.get_by_investigation(investigation_id)
        signals = [
            FraudSignal(
                detector_name=e.detector_name,
                description=e.description,
                severity=e.severity,
                related_account_ids=e.related_account_ids,
                related_transaction_ids=e.related_transaction_ids,
            )
            for e in evidence_list
        ]

        result = self.graph_builder.build(transactions, accounts, signals)
        set_cache(cache_key, result, ttl_seconds=300)
        return result
