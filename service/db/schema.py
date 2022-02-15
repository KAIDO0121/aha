from datetime import datetime
from pydantic import BaseModel
class UserBase(BaseModel): # common fields
    email: str
    name: str

class UserCreate(UserBase): # fields needed for create only
    password: str

class User(UserBase):# fields needed for read only
    id: int
    create_time: datetime

    class Config:
        orm_mode = True
