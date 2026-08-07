from collections import defaultdict

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

MIN_CLUSTER_SIZE = 5  # clusters with 5+ accounts are worth flagging


class DSU:
    """Disjoint Set Union — tracks which accounts belong to the same connected network."""

    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x, y):
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return
        # union by rank — attach smaller tree under bigger tree
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_y] = root_x
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1


class DSUDetector:
    """Flags large connected clusters of accounts (potential fraud rings)."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        dsu = DSU()

        for txn in transactions:
            dsu.union(txn.sender_account_id, txn.receiver_account_id)

        clusters = defaultdict(set)
        for account_id in dsu.parent:
            root = dsu.find(account_id)
            clusters[root].add(account_id)

        signals = []
        for root, members in clusters.items():
            if len(members) >= MIN_CLUSTER_SIZE:
                signals.append(
                    FraudSignal(
                        detector_name="dsu",
                        description=f"Connected network of {len(members)} accounts detected (cluster root: {root})",
                        severity="medium",
                    )
                )

        return signals