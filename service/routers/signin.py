
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
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


TEMPLATES = Jinja2Templates(
    directory=f'{pathlib.Path(__file__).parent.resolve()}/templates')


@router.post("/api/login")
def login_user(user: UserLogin, request: Request, db: Session = Depends(get_db)):
    exist = user_crud.get_user_by_email(db, email=user.email)

    if not exist:
        raise USERNAME_NOT_FOUND
    if not pwd_context.verify(user.password, exist.hashed_password):
        raise WRONG_PASSWORD
    user_crud.update_user_logs(db, exist)

    access_token = auth_handler.encode_token(exist.email, exist.id)
    refresh_token = auth_handler.encode_refresh_token(exist.email, exist.id)
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    return JSONResponse(status_code=200, content={'msg': 'success'})


@router.route("/signin")
def signin(request: Request):
    access_token = request.session.get('access_token')
    if access_token and auth_handler.decode_token(access_token):
        return RedirectResponse('/dashboard')

    return TEMPLATES.TemplateResponse(
        "signin.html",
        {"request": request}
    )
