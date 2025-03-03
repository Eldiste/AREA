from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from src.db.models.base import Base


class UserService(Base):
    __tablename__ = "user_services"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    service_id = Column(BigInteger, ForeignKey("services.id"), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<UserService(id={self.id}, user_id={self.user_id}, service_id={self.service_id})>"

    service = relationship(
        "Service", back_populates="user_services"
    )  # Define the relationship here
