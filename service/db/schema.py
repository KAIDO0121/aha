from datetime import datetime
import re
from pydantic import BaseModel, validator
class UserCreate(BaseModel):  # fields needed for create only
    password: str
    password2: str
    email: str

    @validator('password')
    def password_format(cls, pw):
        find = re.findall(
            r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[-+_!@#$%^&*.,?]).{8,}$", pw)
        if not find:
            raise ValueError('Password must contains...')
        return pw

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
class User(BaseModel):  # fields needed for read only
    id: int
    email: str
    create_time: datetime
    class Config:
        orm_mode = True

class UserLogin(BaseModel): # fields for login request and response
    password: str
    email: str


'''
contains at least one lower character 
contains at least one upper character 
contains at least one digit character 
contains at least one special character
contains at least 8 characters
'''
