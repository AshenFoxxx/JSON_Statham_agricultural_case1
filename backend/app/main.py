from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, models

app = FastAPI(title="АгроЛогистика — Database API")


# ── Pydantic Schemas ─────────────────────────────────────────────

class FarmCreate(BaseModel):
    name: str
    longitude: float
    latitude: float


class FarmResponse(BaseModel):
    id: str
    name: str
    longitude: float
    latitude: float

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    id: str
    name: str
    stock_kg: float = Field(gt=0)
    max_delivery_hours: float = Field(gt=0)


class ProductResponse(BaseModel):
    id: str
    name: str
    stock_kg: float
    max_delivery_hours: float

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    product_id: str
    buyer_id: str
    demand_kg: float = Field(gt=0)
    price_per_kg: float = Field(ge=0)


class OrderResponse(BaseModel):
    id: str
    product_id: str
    buyer_id: str
    demand_kg: float
    price_per_kg: float

    class Config:
        from_attributes = True


class BuyerCreate(BaseModel):
    id: str
    name: str
    longitude: float
    latitude: float


class BuyerResponse(BaseModel):
    id: str
    name: str
    longitude: float
    latitude: float

    class Config:
        from_attributes = True


class VehicleCreate(BaseModel):
    id: str
    name: str
    capacity_kg: float = Field(gt=0)
    fuel_consumption_l_per_100km: float = Field(gt=0)
    fuel_price_rub_per_liter: float = Field(ge=0)
    max_trips: int = Field(ge=1, le=10)
    max_stops: int = Field(ge=1, le=5)
    available: bool = True


class VehicleResponse(BaseModel):
    id: str
    name: str
    capacity_kg: float
    fuel_consumption_l_per_100km: float
    fuel_price_rub_per_liter: float
    max_trips: int
    max_stops: int
    available: bool

    class Config:
        from_attributes = True


# ── Farm ─────────────────────────────────────────────────────────

@app.post("/api/v1/farm", response_model=FarmResponse)
def create_farm(data: FarmCreate, db: Session = Depends(get_db)):
    return crud.create_farm(db, data.name, data.longitude, data.latitude)


@app.get("/api/v1/farm", response_model=FarmResponse)
def get_farm(db: Session = Depends(get_db)):
    farm = crud.get_farm(db)
    if not farm:
        raise HTTPException(status_code=404, detail="Хозяйство не найдено")
    return farm


@app.put("/api/v1/farm", response_model=FarmResponse)
def update_farm(data: FarmCreate, db: Session = Depends(get_db)):
    return crud.update_farm(db, data.name, data.longitude, data.latitude)


# ── Products ─────────────────────────────────────────────────────

@app.post("/api/v1/products", response_model=ProductResponse)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, data.id, data.name, data.stock_kg, data.max_delivery_hours)


@app.get("/api/v1/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return crud.get_products(db)


@app.put("/api/v1/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, data: ProductCreate, db: Session = Depends(get_db)):
    product = crud.update_product(db, product_id, data.name, data.stock_kg, data.max_delivery_hours)
    if not product:
        raise HTTPException(status_code=404, detail="Культура не найдена")
    return product


@app.delete("/api/v1/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db)):
    crud.delete_product(db, product_id)
    return {"message": "Культура удалена"}


# ── Buyers ───────────────────────────────────────────────────────

@app.post("/api/v1/buyers", response_model=BuyerResponse)
def create_buyer(data: BuyerCreate, db: Session = Depends(get_db)):
    return crud.create_buyer(db, data.id, data.name, data.longitude, data.latitude)


@app.get("/api/v1/buyers", response_model=List[BuyerResponse])
def get_buyers(db: Session = Depends(get_db)):
    return crud.get_buyers(db)


@app.put("/api/v1/buyers/{buyer_id}", response_model=BuyerResponse)
def update_buyer(buyer_id: str, data: BuyerCreate, db: Session = Depends(get_db)):
    buyer = crud.update_buyer(db, buyer_id, data.name, data.longitude, data.latitude)
    if not buyer:
        raise HTTPException(status_code=404, detail="Покупатель не найден")
    return buyer


@app.delete("/api/v1/buyers/{buyer_id}")
def delete_buyer(buyer_id: str, db: Session = Depends(get_db)):
    crud.delete_buyer(db, buyer_id)
    return {"message": "Покупатель удалён"}


# ── Orders ───────────────────────────────────────────────────────

@app.post("/api/v1/orders", response_model=OrderResponse)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, data.product_id, data.buyer_id, data.demand_kg, data.price_per_kg)


@app.get("/api/v1/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)


@app.put("/api/v1/orders/{product_id}/{buyer_id}", response_model=OrderResponse)
def update_order(product_id: str, buyer_id: str, data: OrderCreate, db: Session = Depends(get_db)):
    order = crud.update_order(db, product_id, buyer_id, data.demand_kg, data.price_per_kg)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order


@app.delete("/api/v1/orders/{product_id}/{buyer_id}")
def delete_order(product_id: str, buyer_id: str, db: Session = Depends(get_db)):
    crud.delete_order(db, product_id, buyer_id)
    return {"message": "Заказ удалён"}


# ── Vehicles ─────────────────────────────────────────────────────

@app.post("/api/v1/vehicles", response_model=VehicleResponse)
def create_vehicle(data: VehicleCreate, db: Session = Depends(get_db)):
    return crud.create_vehicle(
        db, data.id, data.name, data.capacity_kg,
        data.fuel_consumption_l_per_100km, data.fuel_price_rub_per_liter,
        data.max_trips, data.max_stops, data.available,
    )


@app.get("/api/v1/vehicles", response_model=List[VehicleResponse])
def get_vehicles(db: Session = Depends(get_db)):
    return crud.get_vehicles(db)


@app.put("/api/v1/vehicles/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: str, data: VehicleCreate, db: Session = Depends(get_db)):
    vehicle = crud.update_vehicle(
        db, vehicle_id, data.name, data.capacity_kg,
        data.fuel_consumption_l_per_100km, data.fuel_price_rub_per_liter,
        data.max_trips, data.max_stops, data.available,
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    return vehicle


@app.delete("/api/v1/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    crud.delete_vehicle(db, vehicle_id)
    return {"message": "Машина удалена"}


# ── Health ────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}
