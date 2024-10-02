from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    apartments = relationship("Apartment", back_populates="house")


class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True)
    area = Column(Float)
    house_id = Column(Integer, ForeignKey("houses.id"))
    house = relationship("House", back_populates="apartments")
    meters = relationship("Meter", back_populates="apartment")


class Meter(Base):
    __tablename__ = "meters"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    readings = Column(String)
    apartment_id = Column(Integer, ForeignKey("apartments.id"))
    apartment = relationship("Apartment", back_populates="meters")


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price_per_square_meter = Column(Float)
