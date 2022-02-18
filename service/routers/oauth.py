import os
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, HTMLResponse, JSONResponse
from starlette.config import Config

from authlib.integrations.starlette_client import OAuth, OAuthError

from sqlalchemy.orm import Session

from dotenv import load_dotenv

from db.schema import User as SchemaUser
from db.schema import UserCreate

from crud import user as user_crud

from utils.utils import get_db, CREDENTIALS_EXCEPTION
from utils.auth_bearer import Auth

auth_handler = Auth()
router = APIRouter()
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


@router.route('/api/oauth/google/register_and_login')
async def oauth_login(request: Request):
    redirect_uri = request.url_for('google_oauth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.route('/api/oauth/google')
async def google_oauth(request: Request,  db: Session = next(get_db())): # why use next(get_db()) works??
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise CREDENTIALS_EXCEPTION

    user_data = await oauth.google.parse_id_token(request, access_token)
    exist = user_crud.get_user_by_email(db, email=user_data['email'])
    userid = None
    if exist :
        userid = exist.id
    else:
        user_crud.google_oauth_create_user(db=db, user=user_data)
    token = auth_handler.encode_token( user_data['email'], userid)
    request.session['access_token'] = token
    request.session['verified'] = True
    return RedirectResponse('/dashboard')


@router.route('/api/oauth/facebook/register_and_login')
async def facebook(request: Request):
    redirect_uri = request.url_for('facebook_oauth')
    return await oauth.facebook.authorize_redirect(redirect_uri)


@router.route('/api/oauth/facebook')
async def facebook_oauth(db: Session = next(get_db())):
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
