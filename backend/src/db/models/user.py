from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        BigInteger, Sequence("user_id_seq", start=1, increment=1), primary_key=True
    )
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_oauth = Column(Boolean, default=False)
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
