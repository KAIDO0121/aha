from sqlalchemy.orm import Session

from db.user import User
from db.schema import UserCreate

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    hashed_pw = pwd_context.hash(user.password)
    db_user = User(email=user.email,
                   hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def google_oauth_create_user(db: Session, user: dict):
    db_user = User(email=user['email'],
                   name=user['name'])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


'''
add that instance object to your database session.
commit the changes to the database (so that they are saved).
refresh your instance (so that it contains any new data from the database, like the generated ID).
'''

'''
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

'''
