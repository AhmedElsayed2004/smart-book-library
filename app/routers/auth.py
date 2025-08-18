from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from ..models import User

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = 'ed57a3148dd99969a74eb0a209e00b1638a35ca7c6404a2782c776a89570cd3a'
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# only put tokenUrl for docs
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.password_hash):
        return False
    return user


def create_access_token(role: str, user_id: int, username: str, expires_delta: timedelta):
    encode = {
        'sub': username,
        'exp': datetime.now(timezone.utc) + expires_delta,
        'iat': datetime.now(timezone.utc),
        'role': str(role),
        'id': user_id
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")
        return {'username': username, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")


@router.post("/register")
def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    user = User(username=create_user_request.username,
                email=create_user_request.email,
                password_hash=bcrypt_context.hash(create_user_request.password))
    db.add(user)
    db.commit()


@router.post("/login", response_model=Token)
def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    username = form_data.username
    password = form_data.password

    user = authenticate_user(username, password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")

    token = create_access_token(user.role, user.id, user.username, timedelta(minutes=20))
    response.headers["Authorization"] = f"Bearer {token}"
    return {'access_token': token, 'token_type': 'bearer'}
