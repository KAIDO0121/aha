import os
from datetime import datetime
from datetime import timedelta

import jwt
from fastapi import HTTPException
from fastapi import status

from crud import user

from utils.utils import get_db, cast_to_number, CREDENTIALS_EXCEPTION, INVALID_CREDENTIAL_SCHEME, INVALID_OR_EXPIRED_TOKEN


# Helper to read numbers using var envs



# Configuration
API_SECRET_KEY = os.environ.get('API_SECRET_KEY') or None
if API_SECRET_KEY is None:
    raise BaseException('Missing API_SECRET_KEY env var.')
API_ALGORITHM = os.environ.get('API_ALGORITHM') or 'HS256'
API_ACCESS_TOKEN_EXPIRE_MINUTES = cast_to_number('API_ACCESS_TOKEN_EXPIRE_MINUTES') or 15

# Token url (We should later create a token url that accepts just a user and a password to use it with Swagger)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

# Creating jwt token logics
def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET_KEY, algorithm=API_ALGORITHM)
    return encoded_jwt


# email into jwt token
def create_token(email):
    access_token_expires = timedelta(minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': email}, expires_delta=access_token_expires)
    return access_token


def valid_email_from_db(email):
    exist = user.get_user_by_email(next(get_db()), email=email)
    return exist is not None

# jwt token into email -> being used to access protected api
async def confirm_token_get_email(token: str):
    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=[API_ALGORITHM])
        email = payload.get('sub')
        if email is None:
            raise INVALID_CREDENTIAL_SCHEME
    except jwt.PyJWTError:
        raise INVALID_OR_EXPIRED_TOKEN

    if valid_email_from_db(email):
        return email

    raise CREDENTIALS_EXCEPTION