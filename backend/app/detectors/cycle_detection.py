from collections import defaultdict

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction


class CycleDetectionDetector:
    """Flags cycles in the transaction graph (money flowing back to its origin)."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        graph = defaultdict(set)
        for txn in transactions:
            graph[txn.sender_account_id].add(txn.receiver_account_id)

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
                        )
                    )

        return signals

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