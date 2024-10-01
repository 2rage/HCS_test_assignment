from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string", "format": "objectid"}


class House(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    address: str
    apartments: list

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True


class Tariff(BaseModel):
    name: str
    price_per_square_meter: float

    class Config:
        json_encoders = {ObjectId: str}
        populate_by_name = True
