from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import get_current_user
from src.config import get_db_async_session
from src.db.models import Service, User, UserService
from src.schemas.user_service import UserServiceResponse

router = APIRouter(prefix="/api", tags=["API"])


@router.post("/user_services", response_model=UserServiceResponse)
async def add_user_service(
    user_service: UserServiceResponse,
    session: AsyncSession = Depends(get_db_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Add a new service for the current user.
    """
    new_user_service = UserService(**user_service.dict(), user_id=current_user.id)
    session.add(new_user_service)
    await session.commit()
    await session.refresh(new_user_service)
    return new_user_service


@router.delete("/user_services/{service_id}")
async def delete_user_service(
    service_id: int,
    session: AsyncSession = Depends(get_db_async_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Remove a service connection for the current user.
    """
    result = await session.execute(
        select(UserService)
        .where(UserService.service_id == service_id)
        .where(UserService.user_id == current_user.id)
    )
    user_service = result.scalar_one_or_none()
    if not user_service:
        raise HTTPException(status_code=404, detail="Service not found for the user.")
    await session.delete(user_service)
    await session.commit()
    return {"status": "success"}


@router.get("/user_services/connected", response_model=list[str])
async def get_connected_services(
    session: AsyncSession = Depends(get_db_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get a list of service names that the current user is connected to.
    """
    result = await session.execute(
        select(Service.name)
        .join(UserService, UserService.service_id == Service.id)
        .where(UserService.user_id == current_user.id)
    )
    connected_services = result.scalars().all()
    return connected_services
