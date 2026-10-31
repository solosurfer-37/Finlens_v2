from collections import defaultdict
from collections.abc import Iterator

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

MAX_CYCLES = 50  # safety cap so dense graphs cannot blow up the upload pipeline


class CycleDetectionDetector:
    """Flags cycles in the transaction graph (money flowing back to its origin)."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        graph = defaultdict(set)
        edge_txn_ids = defaultdict(list)
        for txn in transactions:
            graph[txn.sender_account_id].add(txn.receiver_account_id)
            edge_txn_ids[(txn.sender_account_id, txn.receiver_account_id)].append(txn.id)

        signals = []
        seen_cycles = set()

        for start_node in graph:
            for cycle in self._find_cycles(graph, start_node, start_node, []):
                canonical = self._canonical(cycle)
                if canonical in seen_cycles:
                    continue
                seen_cycles.add(canonical)

                path = " -> ".join(str(n) for n in canonical)
                signals.append(
                    FraudSignal(
                        detector_name="cycle_detection",
                        description=f"Circular money flow detected: {path}",
                        severity="high",
                        related_account_ids=list(canonical),
                        related_transaction_ids=self._cycle_txn_ids(list(canonical), edge_txn_ids),
                    )
                )
                if len(signals) >= MAX_CYCLES:
                    return signals

        return signals

    @staticmethod
    def _canonical(cycle: list[int]) -> tuple[int, ...]:
        """Rotate the cycle so it starts at its smallest node (same cycle, same key)."""
        smallest = cycle.index(min(cycle))
        return tuple(cycle[smallest:] + cycle[:smallest])

    @staticmethod
    def _cycle_txn_ids(cycle: list[int], edge_txn_ids: dict) -> list[int]:
        """Transaction ids on the cycle's edges, including the closing edge."""
        txn_ids = []
        for i, node in enumerate(cycle):
            next_node = cycle[(i + 1) % len(cycle)]
            txn_ids.extend(edge_txn_ids.get((node, next_node), []))
        return txn_ids

    def _find_cycles(self, graph, start, current, path) -> Iterator[list[int]]:
        path = path + [current]

        for neighbor in graph.get(current, set()):
            if neighbor == start and len(path) > 1:
                yield path
            elif neighbor not in path:
                yield from self._find_cycles(graph, start, neighbor, path)