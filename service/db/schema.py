from datetime import datetime
import re
from pydantic import BaseModel, validator, root_validator
from pydantic import EmailStr


def password_format(pw: str):
    find = re.findall(
        r"(?=.*\d)", pw)
    if not find:
        raise ValueError(
            "Password must contains at least one digit character")

    find = re.findall(
        r"(?=.*[a-z])(?=.*[A-Z])", pw)
    if not find:
        raise ValueError(
            '''Password must contains contains at least one lower character and one upper character ''')
    find = re.findall(
        r"(?=.*[-+_!@#$%^&*.,?])", pw)
    if not find:
        raise ValueError(
            '''Password must contains at least one special character''')
    find = re.findall(
        r"(?=.{8,}$)", pw)
    if not find:
        raise ValueError(
            '''Password must contains at least 8 characters''')

    return pw


class UserCreate(BaseModel):  # fields needed for create only
    password: str
    password2: str
    email: EmailStr

    _validate_format = validator('password', allow_reuse=True)(password_format)

    @root_validator
    def check_passwords_match(cls, values):
        pw1, pw2 = values.get('password'), values.get('password2')
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return values


class User(BaseModel):  # fields needed for read only
    id: int
    email: str
    create_time: datetime
    login_times: int
    last_login_time: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):  # fields for login request and response
    password: str
    email: EmailStr


class UserEditName(BaseModel):
    name: str

    @validator('name')
    @classmethod
    def name_format(cls, pw):

        find = re.findall(
            r"(?=.*\S.*)", pw)
        if not find:
            raise ValueError('Invalid name')
        return pw


class UserResetPassWord(BaseModel):
    oldpw: str
    password: str
    password2: str

    _validate_format = validator('password', allow_reuse=True)(password_format)

    @root_validator
    def check_passwords_match(cls, values):
        pw1, pw2 = values.get('password'), values.get('password2')
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return values
