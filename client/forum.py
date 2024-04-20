from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from pydantic import BaseModel
from fastapi import HTTPException
DATABASE_URL = "postgresql://ali:password@localhost/authdb"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ForumPost(Base):
    __tablename__ = "forum_posts"
    id = Column(Integer, primary_key=True, index=True)
    userName = Column(String, index=True)
    publicationTime = Column(String)
    avatarResId = Column(String, nullable=True)  # Changed to String to store URLs
    titleText = Column(String, index=True)
    contentImageResId = Column(String, nullable=True)  # Changed to String to store URLs
    contentText = Column(String)

class ForumPostResponseModel(BaseModel):
    id: int
    userName: str
    publicationTime: str
    avatarResId: str | None
    titleText: str
    contentImageResId: str | None
    contentText: str

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DEFAULT_AVATAR_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQIsbG3WjTvP0dl7gg36khwzuX2_ME42mr8PE3OnH37qA&s"
DEFAULT_CONTENT_IMAGE_URL = "https://hips.hearstapps.com/hmg-prod/images/dog-puppy-on-garden-royalty-free-image-1586966191.jpg?crop=0.752xw:1.00xh;0.175xw,0&resize=1200:*"

@app.post("/forum_posts/", response_model=ForumPostResponseModel)
def create_forum_post(userName: str, publicationTime: str, titleText: str, contentText: str, avatarResId: str = None, contentImageResId: str = None, db: Session = Depends(get_db)):
    if not avatarResId:
        avatarResId = DEFAULT_AVATAR_URL
    if not contentImageResId:
        contentImageResId = DEFAULT_CONTENT_IMAGE_URL
    db_forum_post = ForumPost(userName=userName, publicationTime=publicationTime, titleText=titleText, contentText=contentText, avatarResId=avatarResId, contentImageResId=contentImageResId)
    db.add(db_forum_post)
    db.commit()
    db.refresh(db_forum_post)
    return db_forum_post

@app.get("/forum_posts/", response_model=List[ForumPostResponseModel])
def read_forum_posts(db: Session = Depends(get_db)):
    forum_posts = db.query(ForumPost).all()
    return forum_posts

@app.get("/forum_posts/{post_id}", response_model=ForumPostResponseModel)
def read_forum_post(post_id: int, db: Session = Depends(get_db)):
    forum_post = db.query(ForumPost).filter(ForumPost.id == post_id).first()
    if forum_post is None:
        raise HTTPException(status_code=404, detail="Forum post not found")
    return forum_post