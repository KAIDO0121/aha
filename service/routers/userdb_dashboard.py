
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import JSONResponse

from sqlalchemy.orm import Session


from crud import user as user_crud
from utils.utils import get_db

import pathlib

from utils.auth_bearer import Auth


security = HTTPBearer()
auth_handler = Auth()
router = APIRouter()

TEMPLATES = Jinja2Templates(
    directory=f'{pathlib.Path(__file__).parent.resolve()}/templates')


@router.route("/userdb_dashboard")
def userdb_dashboard(request: Request, db: Session = next(get_db())):
    auth_handler.decode_token(request.session.get('access_token'))
    users = user_crud.get_users(db)
    print(users)
    return TEMPLATES.TemplateResponse(
        "userdb_dashboard.html",
        {"request": request, "users": users}
    )
