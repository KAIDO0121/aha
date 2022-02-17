import uvicorn
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, HTMLResponse, JSONResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth, OAuthError

from sqlalchemy.orm import Session

from dotenv import load_dotenv

from db.database import Base, engine 
from db.schema import User as SchemaUser
from db.schema import UserCreate

from crud import user as user_crud

from utils.utils import get_db
from utils.jwt import create_token, valid_email_from_db, CREDENTIALS_EXCEPTION

from routers import sendmail, register

ALLOWED_HOSTS = ["*"]
Base.metadata.create_all(bind=engine)
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DBSessionMiddleware,
                   db_url=os.getenv('DATABASE_URI'))

FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://127.0.0.1:7000/token'
app.include_router(sendmail.router)
app.include_router(register.router)
# OAuth settings
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or None
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')

# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID,
               'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

GOOGLE_SECRET_KEY = os.environ.get('GOOGLE_SECRET_KEY') or None
if GOOGLE_SECRET_KEY is None:
    raise 'Missing GOOGLE_SECRET_KEY'
app.add_middleware(SessionMiddleware, secret_key=GOOGLE_SECRET_KEY)

# Facebook Oauth Config
FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')
oauth.register(
    name='facebook',
    client_id=FACEBOOK_CLIENT_ID,
    client_secret=FACEBOOK_CLIENT_SECRET,
    access_token_url='https://graph.facebook.com/oauth/access_token',
    access_token_params=None,
    authorize_url='https://www.facebook.com/dialog/oauth',
    authorize_params=None,
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email'},
)


@app.route('/api/oauth/google/register_and_login')
async def login(request: Request):
    redirect_uri = request.url_for('google_oauth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/api/oauth/google')
# why use next(get_db()) works??
async def google_oauth(request: Request,  db: Session = next(get_db())):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise CREDENTIALS_EXCEPTION

    user_data = await oauth.google.parse_id_token(request, access_token)
    exist = user_crud.get_user_by_email(db, email=user_data['email'])
    if not exist:
        user_crud.google_oauth_create_user(db=db, user=user_data)

    if valid_email_from_db(user_data['email']):
        return JSONResponse({'result': True, 'access_token': create_token(user_data['email'])})

    raise CREDENTIALS_EXCEPTION



@app.route('/api/oauth/facebook/register_and_login')
async def facebook(request: Request):
    redirect_uri = request.url_for('facebook_oauth')
    return await oauth.facebook.authorize_redirect(redirect_uri)


@app.route('/api/oauth/facebook')
async def facebook_oauth(db: Session = next(get_db())):
    print('bcvbvcbcvbvc')
    try:
        access_token = await oauth.facebook.authorize_access_token()
    except OAuthError:
        return RedirectResponse(url='/fail')

    resp = await oauth.facebook.get(
        'https://graph.facebook.com/me?fields=id,name,email,picture{url}')
    profile = resp.json()
    exist = user_crud.get_user_by_email(db, email=profile['email'])
    if not exist:
        user_crud.google_oauth_create_user(db=db, user=profile)

    return RedirectResponse(url='/')


@app.route('/fail')
def fail(request: Request):
    return Response("Oauth Fail")


@app.get('/')
def public(request: Request):
    user = request.session.get('user')
    if user:
        name = user.get('name')
        return HTMLResponse(f'<p>Hello {name}!</p><a href=/logout>Logout</a>')
    return HTMLResponse('<a href=/api/oauth/google/register_and_login>Login</a>')


@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

if __name__ == "__main__":
    uvicorn.run("main:app", log_level="debug",
                reload=True, port=8000, workers=2,
                ssl_keyfile="./key.pem",
                ssl_certfile="./cert.pem")
