from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from pydantic import BaseModel
from datetime import date
from fastapi import HTTPException

DATABASE_URL = "postgresql://ali:password@localhost/authdb"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_token = Column(String, index=True)
    service_name = Column(String)
    performer_name = Column(String)
    performer_id = Column(Integer)  
    date = Column(String)

class AppointmentResponseModel(BaseModel):
    id: int
    user_token: str
    service_name: str
    performer_name: str
    performer_id: int 
    date: str

class CreateAppointmentModel(BaseModel):
    user_token: str
    service_name: str
    performer_name: str
    performer_id: int
    date: str 

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/appointments/", response_model=AppointmentResponseModel)
def create_appointment(appointment: CreateAppointmentModel, db: Session = Depends(get_db)):
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.get("/appointments/", response_model=List[AppointmentResponseModel])
def read_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()
    return appointments
@app.delete("/appointments/{appointment_id}", response_model=AppointmentResponseModel)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(db_appointment)
    db.commit()
    return db_appointment