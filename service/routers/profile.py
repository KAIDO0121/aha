
from fastapi import APIRouter, Depends
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from sqlalchemy.orm import Session

from service.db.schema import UserEditName

from service.crud import user as user_crud
from service.utils.utils import get_db, CREDENTIALS_EXCEPTION

import pathlib

import os

from service.utils.auth_bearer import Auth

auth_handler = Auth()
router = APIRouter()

TEMPLATES = Jinja2Templates(
    directory=f'{pathlib.Path(__file__).parent.resolve()}/templates')


@router.route("/api/logout")
def logout(request: Request):
    access_token = request.session.get('access_token')
    if not access_token or not auth_handler.decode_token(access_token):
        raise CREDENTIALS_EXCEPTION
    request.session.clear()
    return RedirectResponse(url='/landing')


@router.post("/api/editname")
def editname(user: UserEditName, request: Request, db: Session = Depends(get_db)):
    payload = auth_handler.decode_token(request.session.get('access_token'))
    user_crud.edit_user_name(db, payload['id'], user.name)
    return JSONResponse(status_code=200, content={'msg': 'success'})


@router.route("/profile")
def profile(request: Request):
    payload = auth_handler.decode_token(request.session.get('access_token'))
    user = user_crud.get_user(next(get_db()), payload['id'])

    server_url = os.getenv('SERVER_URL')
    return TEMPLATES.TemplateResponse(
        "profile.html",
        {"request": request, "name": user.name if user else "", "server_url": server_url}
    )
