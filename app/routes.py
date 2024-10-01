from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from app.models import House, Tariff

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["billing_db"]


def serialize_dict(d):
    return {str(k): str(v) if isinstance(v, ObjectId) else v for k, v in d.items()}


def serialize_list(items):
    return [serialize_dict(item) for item in items]


@app.post("/houses/")
async def create_house(house: House):
    result = db.houses.insert_one(house.dict(by_alias=True))
    return {"id": str(result.inserted_id)}


@app.get("/houses/{house_id}")
async def get_house(house_id: str):
    house = db.houses.find_one({"_id": ObjectId(house_id)})
    if not house:
        raise HTTPException(status_code=404, detail="House not found")
    return serialize_dict(house)


@app.get("/houses/")
async def get_all_houses():
    houses = list(db.houses.find())
    return serialize_list(houses)


@app.post("/tariffs/")
async def create_tariff(tariff: Tariff):
    result = db.tariffs.insert_one(tariff.dict(by_alias=True))
    return {"id": str(result.inserted_id)}


@app.get("/tariffs/")
async def get_tariffs():
    tariffs = list(db.tariffs.find())
    return serialize_list(tariffs)
