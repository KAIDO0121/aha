
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, HTMLResponse, JSONResponse
from starlette.config import Config

from sqlalchemy.orm import Session

from db.schema import User as SchemaUser
from db.schema import UserCreate

from crud import user as user_crud
from utils.utils import get_db

from routers.sendmail import send_with_template

import pathlib

from utils.auth_bearer import Auth

security = HTTPBearer()
auth_handler = Auth()
router = APIRouter()

TEMPLATES = Jinja2Templates(directory=f'{pathlib.Path(__file__).parent.resolve()}/templates')

@router.route("/api/confirm/{token}")
def confirm_email(request: Request):
    try:
        payload = auth_handler.decode_token(request.path_params['token'])
    except Exception as e:
        print(e)
        return JSONResponse(status_code=200, content={"message": "The confirmation link is invalid or has expired."})

    db = next(get_db())
    user = user_crud.get_user_by_email(db, email=payload['email'])
    if user.email_verified:
        return JSONResponse(status_code=200, content={"message": "Account already confirmed. Please login."})

    else:
        user.email_verified = True
        db.commit()
        db.refresh(user)
        request.session['verified'] = True
        request.session['access_token'] = request.path_params['token']
        return RedirectResponse(
            url=router.url_path_for('dashboard'),
            status_code=status.HTTP_302_FOUND
        )


@router.post("/api/register", response_model=SchemaUser)
async def create_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    
    exist = user_crud.get_user_by_email(db, email=user.email)
    if exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = user_crud.create_user(db=db, user=user)
    token = auth_handler.encode_token( new_user.email, new_user.id)

    confirm_url = request.url_for('confirm_email', token=token)

    body = {
        "confirm_url": confirm_url,
        "email": user.email
    }

    res = await send_with_template(user.dict(), body)
    request.session['access_token'] = token
    request.session['verified'] = False
    return JSONResponse(status_code=200, content={ 'msg':'success'})


@router.route("/dashboard")
def dashboard(request: Request ):
    print(request.session)
    email = auth_handler.decode_token(request.session.get('access_token'))
    verified = request.session.get('verified')
    if not verified :
        return HTMLResponse(f'<p>This the dashboard</p><a href="/api/send_with_template">Resend Email Verification</a>')
    return HTMLResponse(f'<p>This the dashboard</p>')

@router.route("/signup")
def signup(request: Request):
    return TEMPLATES.TemplateResponse(
        "signup.html",
        {"request": request}
    )
