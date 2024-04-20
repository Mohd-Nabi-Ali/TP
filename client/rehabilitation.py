from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from pydantic import BaseModel

DATABASE_URL = "postgresql://ali:password@localhost/authdb"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Rehabilitation(Base):
    __tablename__ = "rehabilitation"
    id = Column(Integer, primary_key=True, index=True)
    titleText = Column(String, index=True)
    contentImageResId = Column(String, nullable=True)  # Оставляем как String, nullable=True
    contentText = Column(String)


class RehabilitationResponseModel(BaseModel):
    id: int
    titleText: str
    contentText: str
    contentImageResId: str | None

# Создание всех таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
DEFAULT_IMAGE_URL = "https://hips.hearstapps.com/hmg-prod/images/dog-puppy-on-garden-royalty-free-image-1586966191.jpg?crop=0.752xw:1.00xh;0.175xw,0&resize=1200:*"
@app.post("/rehabilitation/", response_model=RehabilitationResponseModel)
def register_worker(titleText: str, contentText: str, contentImageResId: str = None, db: Session = Depends(get_db)):
    if not contentImageResId:
        contentImageResId = DEFAULT_IMAGE_URL
    db_rehabilitation = Rehabilitation(titleText=titleText, contentText=contentText, contentImageResId=contentImageResId)
    db.add(db_rehabilitation)
    db.commit()
    db.refresh(db_rehabilitation)
    return db_rehabilitation

@app.get("/rehabilitation/", response_model=List[RehabilitationResponseModel])
def read_workers(db: Session = Depends(get_db)):
    rehabilitations = db.query(Rehabilitation).all()
    return rehabilitations