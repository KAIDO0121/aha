import os
from fastapi import APIRouter

from datetime import datetime, timedelta

from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.config import Config

from authlib.integrations.starlette_client import OAuth, OAuthError

from sqlalchemy.orm import Session

from service.crud import user as user_crud

from service.utils.utils import get_db, CREDENTIALS_EXCEPTION
from service.utils.auth_bearer import Auth

auth_handler = Auth()
router = APIRouter()


class GoogleOAuth:
    def __init__(self) -> None:

        GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or None
        GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or None
        if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
            raise BaseException('Missing env variables')

        GOOGLE_SECRET_KEY = os.environ.get('GOOGLE_SECRET_KEY') or None

        config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID,
                       'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
        starlette_config = Config(environ=config_data)
        oauth = OAuth(starlette_config)
        oauth.register(
            name='google',
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

        @router.route('/api/oauth/google/register_and_login')
        async def google_oauth_login(request: Request):
            payload = auth_handler.decode_token(request.session.get(
                'access_token'), options={"verify_signature": False})
            print(payload)
            if not payload or payload.get('exp') < datetime.utcnow():
                redirect_uri = request.url_for('google_oauth')
                return await oauth.google.authorize_redirect(request, redirect_uri)
            else:
                return JSONResponse(status_code=200, content={'msg': 'You already login, please logout and try again'})

        @router.route('/api/oauth/google')
        async def google_oauth(request: Request,  db: Session = next(get_db())):
            try:
                access_token = await oauth.google.authorize_access_token(request)
            except OAuthError:
                raise CREDENTIALS_EXCEPTION

            user_data = await oauth.google.parse_id_token(request, access_token)

            exist = user_crud.get_user_by_google_id(
                db, google_id=user_data['sub'])
            userid = None
            if exist:
                user_crud.update_user_logs(db, exist)
                userid = exist.id
            else:
                newuser = user_crud.oauth_create_user(
                    db=db, user=user_data, google_id=user_data['sub'])
                userid = newuser.id
                user_crud.update_user_logs(db, newuser)

            token = auth_handler.encode_token(
                user_data['email'], userid, user_data['name'])
            refresh_token = auth_handler.encode_refresh_token(
                user_data['email'], userid)
            request.session['refresh_token'] = refresh_token
            request.session['access_token'] = token
            request.session['verified'] = True
            return RedirectResponse('/dashboard')


class FacebookOAuth:
    def __init__(self) -> None:
        FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID')
        FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET')

        config_data = {'FACEBOOK_CLIENT_ID': FACEBOOK_CLIENT_ID,
                       'FACEBOOK_CLIENT_SECRET': FACEBOOK_CLIENT_SECRET
                       }
        starlette_config = Config(environ=config_data)
        oauth = OAuth(starlette_config)

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

        @router.route('/api/oauth/facebook/register_and_login')
        async def fb_oauth_login(request: Request):
            payload = auth_handler.decode_token(request.session.get(
                'access_token'), options={"verify_signature": False})
            if not payload or payload.get('exp') < datetime.utcnow():
                redirect_uri = request.url_for('fb_oauth')
                return await oauth.facebook.authorize_redirect(request, redirect_uri)
            else:
                return JSONResponse(status_code=200, content={'msg': 'You already login, please logout and try again'})

        @router.route('/api/oauth/facebook')
        async def fb_oauth(request: Request,  db: Session = next(get_db())):
            try:
                p = await oauth.facebook.authorize_access_token(request)
            except OAuthError:
                raise CREDENTIALS_EXCEPTION

            resp = await oauth.facebook.get(
                'https://graph.facebook.com/me?fields=id,name,email', token=p)
            profile = resp.json()

            exist = user_crud.get_user_by_fb_id(db, fb_id=profile['id'])
            userid = None
            if exist:
                userid = exist.id
                user_crud.update_user_logs(db, exist)
            else:
                newuser = user_crud.oauth_create_user(
                    db=db, user=profile, facebook_id=profile['id'])
                userid = newuser.id
                user_crud.update_user_logs(db, newuser)

            token = auth_handler.encode_token(
                profile['email'], userid, profile['name'])
            refresh_token = auth_handler.encode_refresh_token(
                profile['email'], userid)
            request.session['refresh_token'] = refresh_token
            request.session['access_token'] = token
            request.session['verified'] = True
            return RedirectResponse('/dashboard')


googleOAuth = GoogleOAuth()

facebookOAuth = FacebookOAuth()
