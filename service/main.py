import uvicorn
import os
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv

from service.db.database import Base, engine

from service.utils.auth_bearer import Auth

from service.routers import sendmail, signup, signin, oauth, profile, dashboard, userdb_dashboard

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
SESSION_SECRET = os.getenv('SESSION_SECRET')
app.add_middleware(SessionMiddleware,
                   secret_key=SESSION_SECRET, https_only=True)
app.include_router(sendmail.router)
app.include_router(signup.router)
app.include_router(signin.router)
app.include_router(oauth.router)
app.include_router(profile.router)
app.include_router(dashboard.router)
app.include_router(userdb_dashboard.router)

auth_handler = Auth()


@app.get('/api/refresh_token')
def refresh(request: Request):

    refresh_token = request.session.get('refresh_token')
    new_token = auth_handler.refresh_token(refresh_token)
    request.session['access_token'] = new_token
    return JSONResponse(status_code=200, content={'msg': 'Access token updated'})


@app.route('/landing')
def public(request: Request):
    access_token = request.session.get('access_token')
    if access_token and auth_handler.decode_token(access_token):
        return RedirectResponse('/dashboard')
    return HTMLResponse("<a href='/signup'><button>Sign Up</button></a>  <a href='/signin'><button>Sign In</button></a>")

    # uvicorn.run("main:app", log_level="debug",
    #             reload=True, port=8000, workers=2,
    #             ssl_keyfile="./key.pem",
    #             ssl_certfile="./cert.pem")
