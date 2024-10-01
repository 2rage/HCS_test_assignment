from fastapi import FastAPI, HTTPException
from app.models import House, Tariff
from app.tasks import calculate_bill
from app.database import db
from bson import ObjectId

app = FastAPI()


# Эндпоинт для запуска расчета квартплаты
@app.post("/calculate/{house_id}")
async def start_calculation(house_id: str, month: str, year: int):
    task = calculate_bill.apply_async(args=[house_id, month, year])
    return {"task_id": task.id}


# Эндпоинт для получения прогресса расчета
@app.get("/progress/{task_id}")
async def get_task_progress(task_id: str):
    task = calculate_bill.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.status == "SUCCESS" else None,
    }


# Эндпоинт для получения списка всех домов
@app.get("/houses/")
async def get_houses():
    houses = list(db.houses.find())
    return houses


# Эндпоинт для создания нового дома
@app.post("/houses/")
async def create_house(house: House):
    result = db.houses.insert_one(house.dict(by_alias=True))
    return {"id": str(result.inserted_id)}


# Эндпоинт для получения данных конкретного дома по его ID
@app.get("/houses/{house_id}")
async def get_house(house_id: str):
    house = db.houses.find_one({"_id": ObjectId(house_id)})
    if not house:
        raise HTTPException(status_code=404, detail="House not found")
    return house


# Эндпоинт для получения всех тарифов
@app.get("/tariffs/")
async def get_tariffs():
    return list(db.tariffs.find())


# Эндпоинт для создания нового тарифа
@app.post("/tariffs/")
async def create_tariff(tariff: Tariff):
    result = db.tariffs.insert_one(tariff.dict(by_alias=True))
    return {"id": str(result.inserted_id)}
