from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.auth_controller import AuthController
from app.database.session import get_db
from app.schemas.user_schema import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    controller = AuthController(db)
    return controller.register(data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    controller = AuthController(db)
    return controller.login(data)