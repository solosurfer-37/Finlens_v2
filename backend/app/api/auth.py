from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.controllers.auth_controller import AuthController
from app.core.rate_limiter import limiter
from app.database.session import get_db
from app.schemas.user_schema import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    controller = AuthController(db)
    return controller.register(data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    controller = AuthController(db)
    return controller.login(data)
