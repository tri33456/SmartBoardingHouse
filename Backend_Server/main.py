from fastapi import FastAPI
from pydantic import BaseModel

from datetime import date

from database import SessionLocal, engine
from models import Base, SensorData, Billing

# =====================================
# CREATE TABLES
# =====================================

Base.metadata.create_all(bind=engine)

# =====================================
# FASTAPI
# =====================================

app = FastAPI()

# =====================================
# REQUEST MODEL
# =====================================

class SensorRequest(BaseModel):

    room_id: int

    temperature: float
    humidity: float

    gas: int

    flow_rate: float
    total_water: float

    voltage: float
    current: float
    power: float
    energy: float

# =====================================
# API UPDATE SENSOR
# =====================================

@app.post("/update-sensor")
def update_sensor(data: SensorRequest):

    db = SessionLocal()

    try:

        # =====================================
        # SAVE SENSOR DATA
        # =====================================

        sensor = SensorData(

            room_id=data.room_id,

            temperature=data.temperature,
            humidity=data.humidity,

            gas_value=data.gas,

            water_flow=data.flow_rate,
            total_water=data.total_water,

            voltage=data.voltage,
            current=data.current,
            power=data.power,
            energy=data.energy
        )

        db.add(sensor)

        # =====================================
        # BILLING
        # =====================================

        today = date.today()

        current_month = date(today.year, today.month, 1)

        billing = db.query(Billing).filter(
            Billing.room_id == data.room_id,
            Billing.billing_month == current_month
        ).first()

        # =====================================
        # CALCULATE BILL
        # =====================================

        electric_usage = data.energy

        # đổi L -> m3
        water_usage = data.total_water / 1000.0

        electric_cost = electric_usage * 3500

        water_cost = water_usage * 15000

        total_amount = electric_cost + water_cost

        # =====================================
        # CREATE NEW BILLING
        # =====================================

        if billing is None:

            billing = Billing(

                room_id=data.room_id,

                electric_usage=electric_usage,
                water_usage=water_usage,

                electric_cost=electric_cost,
                water_cost=water_cost,

                total_amount=total_amount,

                billing_month=current_month
            )

            db.add(billing)

        # =====================================
        # UPDATE BILLING
        # =====================================

        else:

            billing.electric_usage = electric_usage

            billing.water_usage = water_usage

            billing.electric_cost = electric_cost

            billing.water_cost = water_cost

            billing.total_amount = total_amount

        # =====================================
        # COMMIT
        # =====================================

        db.commit()

        return {
            "message": "Sensor data and billing updated successfully"
        }

    except Exception as e:

        db.rollback()

        return {
            "error": str(e)
        }

    finally:

        db.close()