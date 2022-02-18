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

from utils.auth_bearer import Auth

from routers import sendmail, register, login, oauth

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
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, https_only=True)
app.include_router(sendmail.router)
app.include_router(register.router)
app.include_router(login.router)
app.include_router(oauth.router)

auth_handler = Auth()


@app.route('/landing')
def public(request: Request):
    return HTMLResponse(f"<a href='/signup'><button>Sign Up</button></a>  <a href='/signin'><button>Sign In</button></a>")


@app.route('/logout')
async def logout(request: Request):
    request.session.pop('access_token', None)
    return RedirectResponse(url='/')

if __name__ == "__main__":
    uvicorn.run("main:app", log_level="debug",
                reload=True, port=8000, workers=2,
                ssl_keyfile="./key.pem",
                ssl_certfile="./cert.pem")
