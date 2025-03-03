from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship to areas
    areas = relationship("Area", back_populates="user")

    # Relationship to services via UserService association table
    services = relationship(
        "Service",
        secondary="user_services",
        back_populates="users",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
