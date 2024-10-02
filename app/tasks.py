from app.database import SessionLocal
from app.models import House, Tariff, Bill
from celery_worker import celery_app
from datetime import datetime


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@celery_app.task(bind=True)
def calculate_bills(self, house_id: int, month: str, year: int):
    db = next(get_db())

    house = db.query(House).filter(House.id == house_id).first()
    if not house:
        raise ValueError(f"Дом с ID {house_id} не найден")

    water_tariff = db.query(Tariff).filter(Tariff.name == "water").first()
    maintenance_tariff = db.query(Tariff).filter(Tariff.name == "maintenance").first()

    if not water_tariff or not maintenance_tariff:
        raise ValueError("Тарифы на воду или содержание общего имущества не найдены")

    total_apartments = len(house.apartments)

    for i, apartment in enumerate(house.apartments):

        maintenance_cost = apartment.area * maintenance_tariff.price_per_square_meter

        water_cost = 0
        for meter in apartment.meters:
            if meter.readings and len(meter.readings.split(",")) >= 2:
                readings = list(map(float, meter.readings.split(",")))
                consumption = readings[-1] - readings[-2]
                water_cost += consumption * water_tariff.price_per_square_meter
            else:
                continue

        total_bill = maintenance_cost + water_cost

        bill = Bill(apartment_id=apartment.id, month=month, year=year, total=total_bill)
        db.add(bill)
        db.commit()

        self.update_state(
            state="PROGRESS", meta={"current": i + 1, "total": total_apartments}
        )

    return {"status": "Calculation completed", "total_apartments": total_apartments}
