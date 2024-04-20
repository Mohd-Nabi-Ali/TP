from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from fastapi.responses import JSONResponse

DATABASE_URL = "postgresql://ali:password@localhost/authdb"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String, unique=True, index=True)
    numberPhone = Column(String, unique=True, index=True)
    image_url = Column(String, index=True, nullable=True)
    hashed_password = Column(String)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)
# Настройки для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

SECRET_KEY = "very_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days = 30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
class UserResponseModel(BaseModel):
    id: int
    username: str
    name: str
    numberPhone: str
    image_url: str | None
app = FastAPI()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
DEFAULT_IMAGE_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQIsbG3WjTvP0dl7gg36khwzuX2_ME42mr8PE3OnH37qA&s"
@app.post("/register/")
def register_user(username: str, password: str,name: str, numberPhone: str,image_url: str = None, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(password)
    if not image_url:
        image_url = DEFAULT_IMAGE_URL
    db_user = User(username=username, hashed_password=hashed_password, name = name, numberPhone = numberPhone, image_url= image_url)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "id": db_user.id, "image_url": db_user.image_url}
@app.get("/users/", response_model=List[UserResponseModel])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return JSONResponse(content={"accessToken": access_token})

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    print(user.image_url)
    return user
@app.get("/users/me/", response_model=UserResponseModel)
def read_current_user(current_user: User = Depends(get_current_user)):
    print( "read " + current_user.image_url)
    return current_user