class FraudSignal:
    """Represents one suspicious finding from a detector."""

    def __init__(
        self,
        detector_name: str,
        description: str,
        severity: str,
        related_account_ids: list[int] | None = None,
        related_transaction_ids: list[int] | None = None,
    ):
        self.detector_name = detector_name
        self.description = description
        self.severity = severity  # "low" | "medium" | "high"
        self.related_account_ids = related_account_ids or []
        self.related_transaction_ids = related_transaction_ids or []

        