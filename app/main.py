from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from pydantic import BaseModel
from app.schemas import (
    HouseResponse,
    HouseCreate,
    TariffResponse,
    TariffCreate,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/houses/", response_model=list[HouseResponse])
def get_houses(db: Session = Depends(get_db)):
    houses = db.query(models.House).all()
    return houses


@app.post("/houses/", response_model=HouseResponse)
def create_house(house: HouseCreate, db: Session = Depends(get_db)):
    new_house = models.House(address=house.address)
    db.add(new_house)
    db.commit()
    db.refresh(new_house)
    return new_house


@app.get("/houses/{house_id}", response_model=HouseResponse)
def get_house(house_id: int, db: Session = Depends(get_db)):
    house = db.query(models.House).filter(models.House.id == house_id).first()
    if not house:
        raise HTTPException(status_code=404, detail="House not found")
    return house


@app.get("/tariffs/", response_model=list[TariffResponse])
def get_tariffs(db: Session = Depends(get_db)):
    tariffs = db.query(models.Tariff).all()
    return tariffs


@app.post("/tariffs/", response_model=TariffResponse)
def create_tariff(tariff: TariffCreate, db: Session = Depends(get_db)):
    new_tariff = models.Tariff(
        name=tariff.name, price_per_square_meter=tariff.price_per_square_meter
    )
    db.add(new_tariff)
    db.commit()
    db.refresh(new_tariff)
    return new_tariff
