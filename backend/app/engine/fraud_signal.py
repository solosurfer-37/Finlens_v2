class FraudSignal:
    """Represents one suspicious finding from a detector."""

    def __init__(self, detector_name: str, description: str, severity: str):
        self.detector_name = detector_name
        self.description = description
        self.severity = severity  # "low" | "medium" | "high"