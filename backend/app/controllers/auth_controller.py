from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import LoginRequest, TokenResponse, UserCreate, UserResponse


class AuthController:
    """
    Handles orchestration for registration and login.
    No direct DB access here — only wiring + business rules.
    """

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(self, data: UserCreate) -> UserResponse:
        existing_user = self.repository.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="A user with this email already exists",
            )

        hashed = hash_password(data.password)
        user = self.repository.create(email=data.email, hashed_password=hashed)
        return UserResponse.model_validate(user)

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.repository.get_by_email(data.email)

        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password",
            )

        token = create_access_token(data={"sub": str(user.id)})
        return TokenResponse(access_token=token)