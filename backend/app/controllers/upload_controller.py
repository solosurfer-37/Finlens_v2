import logging
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.cache import invalidate_investigation_cache
from app.repositories.investigation_repository import InvestigationRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.investigation_schema import InvestigationCreate
from app.services.csv_parser import CSVParseError, parse_transaction_csv
from app.services.file_storage import save_upload
from app.services.transaction_service import TransactionService
from app.engine.detection_engine import DetectionEngine
from app.engine.evidence_engine import EvidenceEngine
from app.engine.report_engine import ReportEngine
from app.schemas.upload_schema import UploadResponse

logger = logging.getLogger(__name__)


class UploadController:
    def __init__(self, db: Session):
        self.db = db
        self.investigation_repo = InvestigationRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.evidence_repo = EvidenceRepository(db)

    def handle_upload(self, file: UploadFile, user_id: int) -> UploadResponse:
        file_path = save_upload(file)
        display_name = Path(file.filename or "").name[:255]

        try:
            rows = parse_transaction_csv(str(file_path))
        except CSVParseError as exc:
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail=str(exc))

        investigation = self.investigation_repo.create(
            InvestigationCreate(filename=display_name),
            user_id=user_id,
        )
        investigation_id = investigation.id

        try:
            transaction_service = TransactionService(self.db, user_id)
            transaction_service.process_rows(investigation_id, rows)

            transactions = self.transaction_repo.get_by_investigation(investigation_id)
            self.investigation_repo.update_transaction_count(investigation_id, len(transactions))

            detection_engine = DetectionEngine(self.db)
            signals = detection_engine.run(transactions)

            evidence_engine = EvidenceEngine(self.db)
            final_score = evidence_engine.process(investigation_id, signals)

            evidence_list = self.evidence_repo.get_by_investigation(investigation_id)
            report_engine = ReportEngine(self.db)
            report_engine.generate(investigation_id, evidence_list)
        except Exception:
            logger.exception("Upload pipeline failed for investigation %s", investigation_id)
            self.db.rollback()
            self.investigation_repo.mark_failed(investigation_id)
            invalidate_investigation_cache(user_id, investigation_id)
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=500,
                detail="Investigation processing failed",
            )

        invalidate_investigation_cache(user_id, investigation_id)

        return UploadResponse(
            investigation_id=investigation_id,
            total_transactions=len(transactions),
            risk_score=float(final_score),
            message="Investigation completed successfully",
        )