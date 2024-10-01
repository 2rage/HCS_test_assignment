from celery import Celery
from app.database import db
from bson import ObjectId

celery_app = Celery("tasks", broker="redis://localhost:6379/0")


@celery_app.task
def calculate_bill(house_id: str, month: str, year: int):
    house = db.houses.find_one({"_id": ObjectId(house_id)})
    if not house:
        raise ValueError("Дом не найден")

    water_tariff = db.tariffs.find_one({"name": "water"})
    maintenance_tariff = db.tariffs.find_one({"name": "maintenance"})

    for apartment in house["apartments"]:
        total = apartment["area"] * maintenance_tariff["price_per_unit"]
        for meter in apartment["meters"]:
            if len(meter["readings"]) >= 2:
                consumption = meter["readings"][-1] - meter["readings"][-2]
                total += consumption * water_tariff["price_per_unit"]

        db.bills.insert_one(
            {
                "apartment_id": apartment["_id"],
                "month": month,
                "year": year,
                "total": total,
            }
        )
