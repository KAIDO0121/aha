from fastapi import FastAPI, Depends, FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware

from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware


from authlib.integrations.starlette_client import OAuth, OAuthError

from sqlalchemy.orm import Session

from dotenv import load_dotenv
import uvicorn
import os

from db.database import Base, engine, SessionLocal  # SessionLocal
from db.schema import User as SchemaUser
from db.schema import UserCreate

from crud import user as user_crud


Base.metadata.create_all(bind=engine)
load_dotenv()
app = FastAPI()
app.add_middleware(DBSessionMiddleware,
                   db_url=os.getenv('DATABASE_URI'))

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

SECRET_KEY = os.environ.get('SECRET_KEY') or None
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


'''
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(endpoint_router, prefix=default_route_str)


@app.on_event("startup")
async def on_app_start():
    """Anything that needs to be done while app starts
    """
    await connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    """Anything that needs to be done while app shutdown
    """
    await close()
'''
# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def home():
    """Home page
    """
    return Response("Hello world")


@app.post("/api/register", response_model=SchemaUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    exist = user_crud.get_user_by_email(db, email=user.email)
    if exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create_user(db=db, user=user)


@app.route('/login')
async def login(request: Request):
    # This creates the url for the /auth endpoint
    return await oauth.google.authorize_redirect(request, '/auth')


@app.route('/auth')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url='/')
    user_data = await oauth.google.parse_id_token(request, access_token)
    request.session['user'] = dict(user_data)
    return RedirectResponse(url='/')


if __name__ == "__main__":
    uvicorn.run("main:app", log_level="debug",
                reload=True, port=8000, workers=2)
