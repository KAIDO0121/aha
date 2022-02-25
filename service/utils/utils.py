from fastapi import Request, HTTPException
from fastapi import status
from db.database import SessionLocal
import os
from pprint import pprint

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def cast_to_number(_id):
    temp = os.environ.get(_id)
    if temp is not None:
        try:
            return float(temp)
        except ValueError:
            return None
    return None


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials.',
    headers={'WWW-Authenticate': 'Bearer'},
)

INVALID_CREDENTIAL_SCHEME = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Invalid authentication scheme.',
    headers={'WWW-Authenticate': 'Bearer'},
)

INVALID_OR_EXPIRED_TOKEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Invalid token or expired token.',
    headers={'WWW-Authenticate': 'Bearer'},
)

USERNAME_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='User name not found'
)

WRONG_PASSWORD = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Wrong password'
)
