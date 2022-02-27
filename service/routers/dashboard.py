
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from sqlalchemy.orm import Session

from db.schema import UserResetPassWord

from crud.user import pwd_context
from crud import user as user_crud

from utils.utils import get_db, WRONG_PASSWORD, NEWPASSWORD_EXISTS
from utils.auth_bearer import Auth

import pathlib

auth_handler = Auth()
router = APIRouter()

TEMPLATES = Jinja2Templates(
    directory=f'{pathlib.Path(__file__).parent.resolve()}/templates')


@router.route("/dashboard")
def dashboard(request: Request):
    payload = auth_handler.decode_token(request.session.get('access_token'))

    verified = request.session.get('verified')
    if not verified:
        return RedirectResponse('/resend_page')
    return TEMPLATES.TemplateResponse(
        "dashboard.html",
        {"request": request, "verified": verified, "name": payload.get('name')}
    )


@router.route("/resend_page")
def resend_page(request: Request):
    auth_handler.decode_token(request.session.get('access_token'))

    return TEMPLATES.TemplateResponse(
        "resend.html",
        {"request": request}
    )


@router.post("/api/resetpassword")
def resetpassword(user: UserResetPassWord, request: Request, db: Session = Depends(get_db)):
    payload = auth_handler.decode_token(request.session.get('access_token'))
    exist = user_crud.get_user_by_email(db, email=payload['email'])

    if not pwd_context.verify(user.oldpw, exist.hashed_password):
        raise WRONG_PASSWORD
    if user.oldpw == user.password:
        raise NEWPASSWORD_EXISTS

    user_crud.reset_user_pw(db, exist, user.password)

    return JSONResponse(status_code=200, content={'msg': 'success'})
