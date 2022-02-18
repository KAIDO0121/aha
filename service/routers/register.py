
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, HTMLResponse, JSONResponse
from starlette.config import Config

import pathlib

from sqlalchemy.orm import Session

from db.schema import User as SchemaUser
from db.schema import UserCreate

from crud import user as user_crud
from utils.jwt import confirm_token_get_email, create_token
from utils.utils import get_db

from routers.sendmail import send_with_template

from utils.auth_bearer import Auth

security = HTTPBearer()
auth_handler = Auth()
router = APIRouter()
templates = Jinja2Templates(directory=f'{pathlib.Path(__file__).parent.resolve()}/templates')

@router.route("/api/confirm/{token}")
async def confirm_email(request: Request):
    try:
        email = await confirm_token_get_email(request.path_params['token'])
    except Exception as e:
        return JSONResponse(status_code=200, content={"message": "The confirmation link is invalid or has expired."})

    db = next(get_db())
    user = user_crud.get_user_by_email(db, email=email)
    if user.email_verified:
        return JSONResponse(status_code=200, content={"message": "Account already confirmed. Please login."})

    else:
        user.email_verified = True
        db.commit()
        db.refresh(user)
        request.session['verified'] = True
        return RedirectResponse(
            url=router.url_path_for("token_callback", token= request.path_params['token']),
            status_code=status.HTTP_302_FOUND
        )

@router.post("/api/register", response_model=SchemaUser)
async def create_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    exist = user_crud.get_user_by_email(db, email=user.email)
    if exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    token = create_token(user.email)

    confirm_url = request.url_for('confirm_email', token=token)

    body = {
        "confirm_url":confirm_url,
        "name":user.name
    }
    # TODO login_user
    res = await send_with_template(user.dict(), body)
    print(res)
    return user_crud.create_user(db=db, user=user)

@router.route("/token_callback/{token}")
def token_callback(request: Request):
    return templates.TemplateResponse("token_callback.html", {"request": request})

@router.get("/dashboard")
def dashboard(request: Request, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    verified= request.session.get('verified')
    email = auth_handler.decode_token(token)
    if not verified :
        return HTMLResponse(f'<p>This the dashboard</p><a href="/api/send_with_template">Resend Email Verification</a>')
    return HTMLResponse(f'<p>This the dashboard</p>')

# GET /users/me 
# -> redirect to get_current_user 
#       check if there's a valid token
# -> redirect to /token
#       use pw and name to get token
# -> return token from /token
# -> get_current_user recieved token
# -> return current_user from get_current_user


# click confirm -> redirecting page -> set jwt token to Bearer Token header
# -> redirect to /dashboard -> read that token

