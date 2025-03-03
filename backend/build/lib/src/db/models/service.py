from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from src.db.models.base import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship to actions and reactions
    actions = relationship("Action", back_populates="service")
    reactions = relationship("Reaction", back_populates="service")

    # Relationship to users via UserService association table
    users = relationship(
        "User",
        secondary="user_services",
        back_populates="services",
    )

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}')>"
