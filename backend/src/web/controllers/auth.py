from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.auth.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
)
from src.auth.utils import get_password_hash, verify_password
from src.config import get_db_async_session
from src.db.accessors.accessor_user import AsyncUserAccessor
from src.db.models import User
from src.schemas.auth import Token, UserConnect
from src.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/auth")


# Register Endpoint
@router.post("/register", response_model=UserResponse, tags=["Auth"])
async def register(
    user: UserCreate, session: AsyncSession = Depends(get_db_async_session)
):
    # Check if username or email already exists
    existing_user_query = await session.execute(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    existing_user = existing_user_query.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Hash the password
    hashed_password = get_password_hash(user.password)

    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
        is_oauth=False,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


# Login Endpoint
@router.post("/login", response_model=Token, tags=["Auth"])
async def login(
    user_connect: UserConnect,
    db: AsyncSession = Depends(get_db_async_session),
):
    # Query user by username or email
    query = await db.execute(
        select(User).where(
            (User.username == user_connect.username_or_email)
            | (User.email == user_connect.username_or_email)
        )
    )
    user = query.scalar_one_or_none()

    # Validate user and password
    if not user or not verify_password(user_connect.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Update User Info Endpoint
@router.put("/user", response_model=UserResponse, tags=["Auth"])
async def update_user_info(
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_db_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Update the current user's information
    """
    updated_user = await AsyncUserAccessor.update_user(
        session=session, user_id=current_user.id, user_data=user_data
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return updated_user


# Get User Email Endpoint
@router.get("/user/email", response_model=dict, tags=["Auth"])
async def get_user_email(current_user: User = Depends(get_current_user)):
    """
    Get the current user's email
    """
    return {"email": current_user.email}
