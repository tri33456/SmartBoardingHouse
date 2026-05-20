from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import Date
from database import Base

class Room(Base):
    __tablename__ = "rooms"

    room_id = Column(Integer, primary_key=True, index=True)
    room_name = Column(String(50))
    status = Column(String(20))

    created_at = Column(TIMESTAMP, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100))
    phone = Column(String(20))

    email = Column(String(100), unique=True)

    password = Column(String(255))

    role = Column(String(20))

    room_id = Column(Integer, ForeignKey("rooms.room_id"), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())


class SensorData(Base):
    __tablename__ = "sensor_data"

    sensor_id = Column(Integer, primary_key=True, index=True)

    room_id = Column(Integer, ForeignKey("rooms.room_id"))

    temperature = Column(Float)
    humidity = Column(Float)

    gas_value = Column(Integer)

    water_flow = Column(Float)
    total_water = Column(Float)

    voltage = Column(Float)
    current = Column(Float)
    power = Column(Float)
    energy = Column(Float)

    created_at = Column(TIMESTAMP, server_default=func.now())


class Billing(Base):
    __tablename__ = "billing"

    bill_id = Column(Integer, primary_key=True, index=True)

    room_id = Column(Integer, ForeignKey("rooms.room_id"))

    electric_usage = Column(Float, default=0)
    water_usage = Column(Float, default=0)

    electric_cost = Column(Float, default=0)
    water_cost = Column(Float, default=0)

    total_amount = Column(Float, default=0)

    billing_month = Column(Date)

    created_at = Column(TIMESTAMP, server_default=func.now())