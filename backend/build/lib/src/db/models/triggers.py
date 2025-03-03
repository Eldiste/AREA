from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from src.db.models.base import Base


class Trigger(Base):
    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # New column for trigger name
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    config = Column(JSON, nullable=False)
    last_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship
    area = relationship("Area", back_populates="trigger")

    def __repr__(self):
        return f"<Trigger(id={self.id}, name={self.name}, area_id={self.area_id})>"
