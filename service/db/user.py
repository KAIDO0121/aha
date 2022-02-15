from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    last_login_time = Column(DateTime(timezone=True), onupdate=func.now())
