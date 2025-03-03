from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from src.db.models.base import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_id = Column(Integer, ForeignKey("actions.id"), nullable=False)
    reaction_id = Column(Integer, ForeignKey("reactions.id"), nullable=False)
    action_config = Column(JSON, nullable=True)
    reaction_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="areas")
    action = relationship("Action", back_populates="areas")
    reaction = relationship("Reaction", back_populates="areas")
    trigger = relationship(
        "Trigger", back_populates="area", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Area(id={self.id}, user_id={self.user_id}, action_id={self.action_id})>"
        )
