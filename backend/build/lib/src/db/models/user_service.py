from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.db.models.base import Base


class UserService(Base):
    __tablename__ = "user_services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    def __repr__(self):
        return f"<UserService(id={self.id}, user_id={self.user_id}, service_id={self.service_id})>"
