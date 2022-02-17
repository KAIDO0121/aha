
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from starlette.requests import Request
from starlette.responses import JSONResponse

from sqlalchemy.orm import Session

from db.schema import User as SchemaUser
from db.schema import UserLogin

from crud import user as user_crud
from utils.utils import get_db, USERNAME_NOT_FOUND, WRONG_PASSWORD

from utils.auth_bearer import Auth

security = HTTPBearer()
auth_handler = Auth()
router = APIRouter()


@router.post("/api/login", response_model=SchemaUser)
async def login_user(user: UserLogin, request: Request, db: Session = Depends(get_db)):

    exist = user_crud.get_user(db, email=user.email)
    if not exist:
        raise USERNAME_NOT_FOUND
    if exist.password != user.password:
        raise WRONG_PASSWORD

    return user_crud.create_user(db=db, user=user)
