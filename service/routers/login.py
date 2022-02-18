
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import JSONResponse
import os
from sqlalchemy.orm import Session

from db.schema import User as SchemaUser
from db.schema import UserLogin

from crud import user as user_crud
from utils.utils import get_db, USERNAME_NOT_FOUND, WRONG_PASSWORD

from utils.auth_bearer import Auth
from crud.user import pwd_context

import pathlib

security = HTTPBearer()
auth_handler = Auth()
router = APIRouter()


TEMPLATES = Jinja2Templates(directory=f'{pathlib.Path(__file__).parent.resolve()}/templates')

@router.post("/api/login")
def login_user(user: UserLogin, request: Request, db: Session = Depends(get_db)):
    exist = user_crud.get_user_by_email(db, email=user.email)

    if not exist:
        raise USERNAME_NOT_FOUND
    if not pwd_context.verify(user.password, exist.hashed_password):
        raise WRONG_PASSWORD
    token = auth_handler.encode_token( exist.email, exist.id)
    request.session['access_token'] = token
    return JSONResponse(status_code=200, content={ 'msg':'success'})

@router.route("/signin")
def login_user(request: Request):
    return TEMPLATES.TemplateResponse(
        "signin.html",
        {"request": request}
    )
