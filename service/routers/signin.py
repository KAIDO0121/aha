
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates

import os

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
import os
from sqlalchemy.orm import Session

from service.db.schema import UserLogin

from service.crud import user as user_crud
from service.utils.utils import get_db, USERNAME_NOT_FOUND, WRONG_PASSWORD

from service.utils.auth_bearer import Auth
from service.crud.user import pwd_context

import pathlib

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
    request.session['verified'] = exist.email_verified
    return JSONResponse(status_code=200, content={'msg': 'success'})


@router.route("/signin")
def signin(request: Request):
    access_token = request.session.get('access_token')
    if access_token:
        return RedirectResponse('/dashboard')
    server_url = os.getenv('SERVER_URL')
    return TEMPLATES.TemplateResponse(
        "signin.html",
        {"request": request, "server_url": server_url}
    )
