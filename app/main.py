from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from app.schemas import (
    HouseResponse,
    HouseCreate,
    TariffResponse,
    TariffCreate,
    ApartmentCreate,
    ApartmentResponse,
    HouseDetailResponse,
)
from celery.result import AsyncResult
from app.tasks import calculate_bills
from app.models import Bill, Apartment

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


@app.get("/houses/{house_id}/detail", response_model=HouseDetailResponse)
async def get_house_detail(house_id: int, db: Session = Depends(get_db)):
    house = db.query(models.House).filter(models.House.id == house_id).first()

    if not house:
        raise HTTPException(status_code=404, detail="House not found")

    total_area = sum(apartment.area for apartment in house.apartments)
    total_meters = sum(len(apartment.meters) for apartment in house.apartments)

    return {
        "id": house.id,
        "address": house.address,
        "total_area": total_area,
        "total_meters": total_meters,
        "apartments": house.apartments,
    }


@app.post("/houses/{house_id}/apartments/", response_model=ApartmentResponse)
def create_apartment(
    house_id: int, apartment: ApartmentCreate, db: Session = Depends(get_db)
):
    house = db.query(models.House).filter(models.House.id == house_id).first()

    if not house:
        raise HTTPException(status_code=404, detail="House not found")

    new_apartment = models.Apartment(area=apartment.area, house_id=house_id)
    db.add(new_apartment)
    db.commit()
    db.refresh(new_apartment)

    for meter_data in apartment.meters:
        new_meter = models.Meter(type=meter_data.type, apartment_id=new_apartment.id)
        db.add(new_meter)

    db.commit()

    return new_apartment


@app.post("/calculate/{house_id}")
async def start_calculation(house_id: int, month: str, year: int):
    task = calculate_bills.apply_async(args=[house_id, month, year])
    return {"task_id": task.id}


@app.get("/progress/{task_id}")
async def get_task_progress(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == "PROGRESS":
        return {
            "task_id": task_id,
            "status": task_result.state,
            "progress": task_result.info,
        }
    else:
        return {
            "task_id": task_id,
            "status": task_result.state,
            "result": task_result.info,
        }


@app.get("/bills/{house_id}")
def get_bills(house_id: int, db: Session = Depends(get_db)):
    bills = db.query(Bill).join(Apartment).filter(Apartment.house_id == house_id).all()

    if not bills:
        raise HTTPException(status_code=404, detail="Для этого дома нет расчетов ЖКУ")

    return bills
