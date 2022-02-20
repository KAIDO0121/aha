from sqlalchemy.orm import Session
from datetime import datetime
from db.user import User
from db.schema import UserCreate, UserResetPassWord

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def edit_user_name(db: Session, user_id: int, newname: str):
    user = db.query(User).filter(User.id == user_id).first()
    user.name = newname
    db.commit()


def update_user_logs(db: Session, user: User):
    user.login_times += 1
    user.last_login_time = datetime()
    db.commit()


def reset_user_pw(db: Session, user: User, newpassword: str):
    hashed_pw = pwd_context.hash(newpassword)
    user.hashed_password = hashed_pw
    db.commit()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session):
    return db.query(User).with_entities(User.id, User.create_time, User.login_times, User.last_login_time).all()


def create_user(db: Session, user: UserCreate):
    hashed_pw = pwd_context.hash(user.password)
    db_user = User(email=user.email,
                   hashed_password=hashed_pw,
                   login_times=1)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def oauth_create_user(db: Session, user: dict, **kwargs):
    _id = kwargs.get('google_id')
    if _id:
        db_user = User(email=user['email'],
                       google_id=_id,
                       name=user['name'],
                       login_times=1
                       )
    else:
        db_user = User(email=user['email'],
                       facebook_id=kwargs.get('facebook_id'),
                       name=user['name'],
                       login_times=1)
    db.add(db_user)
    db.commit()
