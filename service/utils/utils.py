from fastapi import HTTPException
from fastapi import status
from service.db.database import SessionLocal
import os


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
    detail='Token expired, please try login again.',
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

NEWPASSWORD_EXISTS = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="You can't use old password as new password"
)

EMAIL_EXISTS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email already registered"
)
