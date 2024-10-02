from pydantic import BaseModel


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
