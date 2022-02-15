from fastapi import FastAPI, Depends, FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware, db
from starlette.requests import Request
from starlette.responses import Response

from sqlalchemy.orm import Session

from dotenv import load_dotenv
import uvicorn
import os

from db.database import Base, engine, SessionLocal # SessionLocal
from db.schema import User as SchemaUser
from db.schema import UserCreate

from crud import user as user_crud


Base.metadata.create_all(bind=engine)
load_dotenv()
app = FastAPI()
app.add_middleware(DBSessionMiddleware,
                   db_url=os.getenv('DATABASE_URI'))

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


if __name__ == "__main__":
    uvicorn.run("main:app", log_level="debug", reload=True, port=8000, workers=2)
