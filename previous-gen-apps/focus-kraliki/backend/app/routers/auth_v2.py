from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    generate_id
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserWithToken
from app.services.knowledge_defaults import ensure_default_item_types
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/auth/v2", tags=["auth"])

@router.post("/register", response_model=UserWithToken)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        id=generate_id(),
        email=user_data.email,
        username=user_data.name,
        firstName=user_data.name.split()[0] if user_data.name else None,
        passwordHash=get_password_hash(user_data.password),
        organizationId=generate_id()  # Create default org
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize default knowledge item types for new user
    ensure_default_item_types(user.id, db)

    # Ensure workspace + membership exists
    WorkspaceService.ensure_default_workspace(user, db)

    # Create token
    access_token = create_access_token(data={"sub": user.id})

    return UserWithToken(
        user=UserResponse.model_validate(user),
        token=access_token,
        access_token=access_token,
    )

@router.post("/login", response_model=UserWithToken)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not user.passwordHash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(credentials.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Make sure workspace context exists for legacy users
    WorkspaceService.ensure_default_workspace(user, db)

    access_token = create_access_token(data={"sub": user.id})

    return UserWithToken(
        user=UserResponse.model_validate(user),
        token=access_token,
        access_token=access_token,
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # In a real app, you'd invalidate the token here
    return {"success": True, "message": "Logged out successfully"}
