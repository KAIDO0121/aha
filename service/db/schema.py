from datetime import datetime
import re
from pydantic import BaseModel, ValidationError, validator
class UserBase(BaseModel): # common fields
    email: str
    name: str

class UserCreate(UserBase): # fields needed for create only
    password: str
    password2: str

    @validator('password')
    def password_format(cls, pw):
        find = re.findall(r"(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[-+_!@#$%^&*.,?]).{8,}$", pw)
        if not find:
            raise ValueError('Password must contains...')
        return pw

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

class User(UserBase):# fields needed for read only
    id: int
    create_time: datetime

    class Config:
        orm_mode = True

'''
contains at least one lower character 
contains at least one upper character 
contains at least one digit character 
contains at least one special character
contains at least 8 characters
'''

