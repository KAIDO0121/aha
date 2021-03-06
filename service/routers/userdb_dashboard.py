
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from starlette.requests import Request

from sqlalchemy.orm import Session

from collections import namedtuple

from service.crud import user as user_crud
from service.utils.utils import get_db

import pathlib

from service.utils.auth_bearer import Auth

auth_handler = Auth()
router = APIRouter()

TEMPLATES = Jinja2Templates(
    directory=f'{pathlib.Path(__file__).parent.resolve()}/templates')


@router.route("/userdb_dashboard")
def userdb_dashboard(request: Request, db: Session = next(get_db())):
    auth_handler.decode_token(request.session.get('access_token'))
    Record = namedtuple(
        "Record", ["userid", "signuptime", "logintimes", "lastlogin"])

    _users = user_crud.get_users_db_dashboard(db)
    today_session = user_crud.get_today_session_users(db)
    avg_per_day = user_crud.get_average_session_user_per_day(db)

    users = []
    for user in _users:
        obj = Record(*user)._asdict()

        obj['signuptime'] = obj['signuptime'].strftime("%Y-%m-%d, %H:%M:%S")
        obj['lastlogin'] = obj['lastlogin'].strftime("%Y-%m-%d, %H:%M:%S")
        users.append(obj)

    return TEMPLATES.TemplateResponse(
        "userdb_dashboard.html",
        {"request": request, "users": users,
         "signup_count": len(
             _users), "today_session": today_session, "avg_per_day": avg_per_day}
    )
