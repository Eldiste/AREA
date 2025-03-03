from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import get_db_async_session
from ...db.accessors.area_accessor import AsyncAreaAccessor
from ...schemas.area import AreaCreate, AreaResponse
from .main import app


@app.post("/areas/", response_model=AreaResponse)
async def create_area(
    area_data: AreaCreate, db: AsyncSession = Depends(get_db_async_session)
):
    """
    Create a new AREA linking an Action, Reaction, and Trigger.
    """
    area = await AsyncAreaAccessor.create_area(db, area_data)
    if not area:
        raise HTTPException(status_code=400, detail="Failed to create AREA.")
    return area


@app.get("/areas/{area_id}/", response_model=AreaResponse)
async def get_area(area_id: int, db: AsyncSession = Depends(get_db_async_session)):
    """
    Get details of a specific AREA.
    """
    area = await AsyncAreaAccessor.get_area_by_id(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="AREA not found.")
    return area


@app.delete("/areas/{area_id}/", status_code=204)
async def delete_area(area_id: int, db: AsyncSession = Depends(get_db_async_session)):
    """
    Delete an AREA by ID.
    """
    success = await AsyncAreaAccessor.delete_area(db, area_id)
    if not success:
        raise HTTPException(status_code=404, detail="AREA not found.")
