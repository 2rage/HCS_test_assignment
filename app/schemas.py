from pydantic import BaseModel
from typing import List


class HouseBase(BaseModel):
    address: str


class HouseCreate(HouseBase):
    pass


class HouseResponse(HouseBase):
    id: int

    class Config:
        orm_mode = True


class TariffBase(BaseModel):
    name: str
    price_per_square_meter: float


class TariffCreate(TariffBase):
    pass


class TariffResponse(TariffBase):
    id: int

    class Config:
        orm_mode = True


class MeterResponse(BaseModel):
    id: int
    type: str

    class Config:
        orm_mode = True


class MeterCreate(BaseModel):
    type: str  # Тип счетчика, например "water", "electricity", "gas"


# Pydantic модель для квартиры (Apartment)
class ApartmentResponse(BaseModel):
    id: int
    area: float
    meters: List[MeterResponse]

    class Config:
        orm_mode = True


class ApartmentCreate(BaseModel):
    area: float  # Площадь квартиры
    meters: List[MeterCreate]

    class Config:
        orm_mode = True


class HouseDetailResponse(BaseModel):
    id: int
    address: str
    total_area: float
    total_meters: int
    apartments: List[ApartmentResponse]

    class Config:
        orm_mode = True
