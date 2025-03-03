import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_db_async_session
from src.db.models import User
from src.schemas.auth import TokenData

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
LOGGER = logging.getLogger(__name__)

if not SECRET_KEY or not ALGORITHM:
    raise ValueError(
        "SECRET_KEY and ALGORITHM must be set in the environment variables."
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        LOGGER.warning(
            f"Decoding token with Secret: {SECRET_KEY} | Algorithm: {ALGORITHM}"
        )
        LOGGER.warning(f"Token to decode: {token}")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        LOGGER.warning(f"Decoded Payload: {payload}")

        username: str = payload.get("sub")
        LOGGER.warning(f"Username extracted: {username}")

        if username is None:
            raise credentials_exception

        return TokenData(username=username)
    except ExpiredSignatureError:
        LOGGER.error("Token has expired")
        raise credentials_exception
    except JWTError as e:
        LOGGER.error(f"JWT decode error: {e}")
        raise credentials_exception


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_async_session),
) -> User:
    token = credentials.credentials

    payload = decode_access_token(token)
    if not payload or not payload.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        query = await db.execute(select(User).where(User.username == payload.username))
        user = query.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(e)}",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"Authenticated user: {user.username}")
    return user
