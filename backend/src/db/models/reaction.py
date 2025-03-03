from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from src.db.models.base import Base


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship
    service = relationship("Service", back_populates="reactions")
    areas = relationship("Area", back_populates="reaction")

    def __repr__(self):
        return f"<Reaction(id={self.id}, name='{self.name}')>"
