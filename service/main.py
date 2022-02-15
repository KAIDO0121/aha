from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db
from starlette.requests import Request
from starlette.responses import Response

from service.db.database import Base, engine
import uvicorn
import os

from db.schema import User as SchemaUser
from db.user import User as ModelUser

from passlib.context import CryptContext

from dotenv import load_dotenv


load_dotenv()
app = FastAPI()
app.add_middleware(DBSessionMiddleware,
                   db_url=os.getenv('DATABASE_URI'))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


@app.get("/")
async def home():
    """Home page
    """
    return Response("Hello world")


@app.post('/register', response_model=SchemaUser)
async def register(user: SchemaUser):
    hashed_pw = pwd_context.hash(user.password)
    db_user = ModelUser(email=user.email,
                        name=user.name,
                        hashed_password=hashed_pw)
    db.session.add(db_user)
    db.session.commit()
    return db_user


if __name__ == "__main__":
    uvicorn.run(app, log_level="debug", reload=True, port=8000)
