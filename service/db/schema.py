from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    email: str
    hashed_password: str
    name: str

    class Config:
        orm_mode = True
