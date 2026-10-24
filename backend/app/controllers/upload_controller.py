from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.repositories.investigation_repository import InvestigationRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.investigation_schema import InvestigationCreate
from app.services.csv_parser import parse_transaction_csv
from app.services.file_storage import save_upload
from app.services.transaction_service import TransactionService
from app.engine.detection_engine import DetectionEngine
from app.engine.evidence_engine import EvidenceEngine
from app.engine.report_engine import ReportEngine
from app.schemas.upload_schema import UploadResponse


class UploadController:
    def __init__(self, db: Session):
        self.db = db
        self.investigation_repo = InvestigationRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.evidence_repo = EvidenceRepository(db)

    def handle_upload(self, file: UploadFile) -> UploadResponse:
        file_path = save_upload(file)
        display_name = Path(file.filename or "").name[:255]

        investigation = self.investigation_repo.create(
            InvestigationCreate(filename=display_name)
        )

        rows = parse_transaction_csv(str(file_path))
        transaction_service = TransactionService(self.db)
        transaction_service.process_rows(investigation.id, rows)

        transactions = self.transaction_repo.get_by_investigation(investigation.id)
        self.investigation_repo.update_transaction_count(investigation.id, len(transactions))

        detection_engine = DetectionEngine(self.db)
        signals = detection_engine.run(transactions)

        evidence_engine = EvidenceEngine(self.db)
        final_score = evidence_engine.process(investigation.id, signals)

        evidence_list = self.evidence_repo.get_by_investigation(investigation.id)
        report_engine = ReportEngine(self.db)
        report_engine.generate(investigation.id, evidence_list)

        return UploadResponse(
            investigation_id=investigation.id,
            total_transactions=len(transactions),
            risk_score=float(final_score),
            message="Investigation completed successfully",
        )