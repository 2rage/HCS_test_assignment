from celery import Celery
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import House, Tariff

celery_app = Celery("tasks", broker="redis://localhost:6379/0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@celery_app.task
def calculate_bill(house_id: int, month: str, year: int):
    db: Session = next(get_db())
    house = db.query(House).filter(House.id == house_id).first()
    if not house:
        raise ValueError("Дом не найден")

    water_tariff = db.query(Tariff).filter(Tariff.name == "water").first()
    maintenance_tariff = db.query(Tariff).filter(Tariff.name == "maintenance").first()

    for apartment in house.apartments:
        total = apartment.area * maintenance_tariff.price_per_square_meter
        for meter in apartment.meters:
            readings = list(map(float, meter.readings.split(",")))
            if len(readings) >= 2:
                consumption = readings[-1] - readings[-2]
                total += consumption * water_tariff.price_per_square_meter

        db.commit()
