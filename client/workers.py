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

class Worker(Base):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True, index=True)
    workerName = Column(String, index=True)
    workerResId = Column(String, nullable=True)  # Оставляем как String, nullable=True
    workerCost = Column(String)
    workerService = Column(String)
    workerExperience = Column(String)
    workerInfo = Column(String)

class WorkerResponseModel(BaseModel):
    id: int
    workerName: str
    workerCost: str
    workerService: str
    workerExperience: str
    workerInfo: str
    workerResId: str | None

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
DEFAULT_IMAGE_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQIsbG3WjTvP0dl7gg36khwzuX2_ME42mr8PE3OnH37qA&s"
@app.post("/workers/", response_model=WorkerResponseModel)
def register_worker(workerName: str, workerCost: str, workerService: str, workerExperience: str, workerInfo: str, workerResId: str = None ,db: Session = Depends(get_db)):
    if not workerResId:
        workerResId = DEFAULT_IMAGE_URL
    db_worker = Worker(workerName=workerName, workerResId=workerResId, workerCost=workerCost, workerService=workerService, workerExperience=workerExperience, workerInfo=workerInfo)
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker

@app.get("/workers/", response_model=List[WorkerResponseModel])
def read_workers(db: Session = Depends(get_db)):
    workers = db.query(Worker).all()
    return workers

@app.get("/workers/{worker_id}", response_model=WorkerResponseModel)
def read_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker