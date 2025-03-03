from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.db.models.user import User
from src.schemas.user import UserCreate, UserResponse, UserUpdate


class UserAccessor:

    @staticmethod
    def create_user(
        session: Session, user_data: UserCreate, hashed_password: str
    ) -> UserResponse:
        """
        Create a new user with the given data.
        """
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return UserResponse.from_orm(new_user)

    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> Optional[UserResponse]:
        """
        Retrieve a user by ID.
        """
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return UserResponse.from_orm(user)
        return None

    @staticmethod
    def update_user(
        session: Session, user_id: int, user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """
        Update a user with the provided data.
        """
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        session.commit()
        session.refresh(user)
        return UserResponse.from_orm(user)

    @staticmethod
    def delete_user(session: Session, user_id: int) -> bool:
        """
        Delete a user by ID.
        """
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        session.delete(user)
        session.commit()
        return True


# Asynchronous CRUD
class AsyncUserAccessor:

    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreate) -> UserResponse:
        """
        Create a new user with the given data.
        """
        user_dict = user_data.dict(exclude={"password"})
        new_user = User(
            username=user_dict["username"],
            email=user_dict["email"],
            hashed_password=None if user_data.is_oauth else user_data.password,
            is_oauth=user_data.is_oauth,
            is_active=True,
            is_admin=False,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return UserResponse.from_orm(new_user)

    @staticmethod
    async def get_user_by_id(
        session: AsyncSession, user_id: int
    ) -> Optional[UserResponse]:
        """
        Retrieve a user by ID.
        """
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            return UserResponse.from_orm(user)
        return None

    @staticmethod
    async def update_user(
        session: AsyncSession, user_id: int, user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """
        Update a user with the provided data.
        """
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)
        return UserResponse.from_orm(user)

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int) -> bool:
        """
        Delete a user by ID.
        """
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True

    @staticmethod
    async def get_user_by_email(
        session: AsyncSession, email: str
    ) -> Optional[UserResponse]:
        """
        Retrieve a user by email.
        """
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return UserResponse.from_orm(user)
        return None
