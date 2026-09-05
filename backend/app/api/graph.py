from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.graph_controller import GraphController
from app.database.session import get_db

router = APIRouter(prefix="/investigations", tags=["Graph"])


@router.get("/{investigation_id}/graph")
def get_graph(investigation_id: int, db: Session = Depends(get_db)):
    controller = GraphController(db)
    return controller.get_graph(investigation_id)