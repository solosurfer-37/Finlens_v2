from collections import defaultdict

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction


class CycleDetectionDetector:
    """Flags cycles in the transaction graph (money flowing back to its origin)."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        graph = defaultdict(set)
        edge_txn_ids = defaultdict(list)
        for txn in transactions:
            graph[txn.sender_account_id].add(txn.receiver_account_id)
            edge_txn_ids[(txn.sender_account_id, txn.receiver_account_id)].append(txn.id)

        signals = []
        visited_cycles = set()

        for start_node in graph:
            cycle = self._find_cycle(graph, start_node, start_node, set())
            if cycle:
                cycle_key = frozenset(cycle)
                if cycle_key not in visited_cycles:
                    visited_cycles.add(cycle_key)
                    path = " -> ".join(str(n) for n in cycle)
                    signals.append(
                        FraudSignal(
                            detector_name="cycle_detection",
                            description=f"Circular money flow detected: {path}",
                            severity="high",
                            related_account_ids=list(cycle),
                            related_transaction_ids=self._cycle_txn_ids(cycle, edge_txn_ids),
                        )
                    )

        return signals

    @staticmethod
    def _cycle_txn_ids(cycle: list[int], edge_txn_ids: dict) -> list[int]:
        """Transaction ids on the cycle's edges, including the closing edge."""
        txn_ids = []
        for i, node in enumerate(cycle):
            next_node = cycle[(i + 1) % len(cycle)]
            txn_ids.extend(edge_txn_ids.get((node, next_node), []))
        return txn_ids

    def _find_cycle(self, graph, start, current, visited, path=None):
        if path is None:
            path = []

        path = path + [current]
        visited = visited | {current}

        for neighbor in graph.get(current, set()):
            if neighbor == start and len(path) > 1:
                return path
            if neighbor not in visited:
                result = self._find_cycle(graph, start, neighbor, visited, path)
                if result:
                    return result

        return None