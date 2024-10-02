from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import engine, SessionLocal
from app.schemas import HouseCreate, TariffCreate

app = FastAPI()


models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/houses/")
async def create_house(house: HouseCreate, db: Session = Depends(get_db)):
    new_house = models.House(address=house.address)
    db.add(new_house)
    db.commit()
    db.refresh(new_house)

    for apartment in house.apartments:
        new_apartment = models.Apartment(area=apartment.area, house_id=new_house.id)
        db.add(new_apartment)

    db.commit()

    return {"id": new_house.id, "address": new_house.address}


@app.get("/houses/{house_id}")
async def get_house(house_id: int, db: Session = Depends(get_db)):
    house = db.query(models.House).filter(models.House.id == house_id).first()
    if not house:
        raise HTTPException(status_code=404, detail="House not found")
    return house


@app.get("/houses/")
async def get_houses(db: Session = Depends(get_db)):
    houses = db.query(models.House).all()
    return houses


@app.post("/tariffs/")
async def create_tariff(tariff: TariffCreate, db: Session = Depends(get_db)):
    new_tariff = models.Tariff(
        name=tariff.name, price_per_square_meter=tariff.price_per_square_meter
    )
    db.add(new_tariff)
    db.commit()
    db.refresh(new_tariff)
    return {"id": new_tariff.id}


@app.get("/tariffs/")
async def get_tariffs(db: Session = Depends(get_db)):
    tariffs = db.query(models.Tariff).all()
    return tariffs
