from sqlalchemy.orm import Session
from app.models import Farm, Product, Buyer, BuyerOrder, Vehicle


# ── Farm ──────────────────────────────────────────────────────────

def create_farm(db: Session, name: str, longitude: float, latitude: float) -> Farm:
    farm = Farm(id="farm", name=name, longitude=longitude, latitude=latitude)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


def get_farm(db: Session) -> Farm | None:
    return db.query(Farm).first()


def update_farm(db: Session, name: str, longitude: float, latitude: float) -> Farm:
    farm = db.query(Farm).first()
    if farm:
        farm.name = name
        farm.longitude = longitude
        farm.latitude = latitude
    else:
        farm = Farm(id="farm", name=name, longitude=longitude, latitude=latitude)
        db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


# ── Product ───────────────────────────────────────────────────────

def create_product(db: Session, id: str, name: str, stock_kg: float, max_delivery_hours: float) -> Product:
    product = Product(id=id, name=name, stock_kg=stock_kg, max_delivery_hours=max_delivery_hours)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_products(db: Session) -> list[Product]:
    return db.query(Product).all()


def update_product(db: Session, id: str, name: str, stock_kg: float, max_delivery_hours: float) -> Product:
    product = db.query(Product).filter(Product.id == id).first()
    if product:
        product.name = name
        product.stock_kg = stock_kg
        product.max_delivery_hours = max_delivery_hours
        db.commit()
        db.refresh(product)
    return product


def delete_product(db: Session, id: str):
    product = db.query(Product).filter(Product.id == id).first()
    if product:
        db.delete(product)
        db.commit()


# ── Buyer ─────────────────────────────────────────────────────────

def create_buyer(db: Session, id: str, name: str, longitude: float, latitude: float) -> Buyer:
    buyer = Buyer(id=id, name=name, longitude=longitude, latitude=latitude)
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


def get_buyers(db: Session) -> list[Buyer]:
    return db.query(Buyer).all()


def update_buyer(db: Session, id: str, name: str, longitude: float, latitude: float) -> Buyer:
    buyer = db.query(Buyer).filter(Buyer.id == id).first()
    if buyer:
        buyer.name = name
        buyer.longitude = longitude
        buyer.latitude = latitude
        db.commit()
        db.refresh(buyer)
    return buyer


def delete_buyer(db: Session, id: str):
    buyer = db.query(Buyer).filter(Buyer.id == id).first()
    if buyer:
        db.delete(buyer)
        db.commit()


# ── BuyerOrder ────────────────────────────────────────────────────

def create_order(db: Session, product_id: str, buyer_id: str, demand_kg: float, price_per_kg: float) -> BuyerOrder:
    order = BuyerOrder(
        id=f"order-{product_id}-{buyer_id}",
        product_id=product_id,
        buyer_id=buyer_id,
        demand_kg=demand_kg,
        price_per_kg=price_per_kg,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_orders(db: Session) -> list[BuyerOrder]:
    return db.query(BuyerOrder).all()


def update_order(db: Session, product_id: str, buyer_id: str, demand_kg: float, price_per_kg: float) -> BuyerOrder:
    order = db.query(BuyerOrder).filter(
        BuyerOrder.product_id == product_id,
        BuyerOrder.buyer_id == buyer_id,
    ).first()
    if order:
        order.demand_kg = demand_kg
        order.price_per_kg = price_per_kg
        db.commit()
        db.refresh(order)
    return order


def delete_order(db: Session, product_id: str, buyer_id: str):
    order = db.query(BuyerOrder).filter(
        BuyerOrder.product_id == product_id,
        BuyerOrder.buyer_id == buyer_id,
    ).first()
    if order:
        db.delete(order)
        db.commit()


# ── Vehicle ───────────────────────────────────────────────────────

def create_vehicle(db: Session, id: str, name: str, capacity_kg: float,
                   fuel_consumption_l_per_100km: float, fuel_price_rub_per_liter: float,
                   max_trips: int, max_stops: int, available: bool) -> Vehicle:
    vehicle = Vehicle(
        id=id, name=name, capacity_kg=capacity_kg,
        fuel_consumption_l_per_100km=fuel_consumption_l_per_100km,
        fuel_price_rub_per_liter=fuel_price_rub_per_liter,
        max_trips=max_trips, max_stops=max_stops, available=available,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def get_vehicles(db: Session) -> list[Vehicle]:
    return db.query(Vehicle).all()


def update_vehicle(db: Session, id: str, name: str, capacity_kg: float,
                   fuel_consumption_l_per_100km: float, fuel_price_rub_per_liter: float,
                   max_trips: int, max_stops: int, available: bool) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.id == id).first()
    if vehicle:
        vehicle.name = name
        vehicle.capacity_kg = capacity_kg
        vehicle.fuel_consumption_l_per_100km = fuel_consumption_l_per_100km
        vehicle.fuel_price_rub_per_liter = fuel_price_rub_per_liter
        vehicle.max_trips = max_trips
        vehicle.max_stops = max_stops
        vehicle.available = available
        db.commit()
        db.refresh(vehicle)
    return vehicle


def delete_vehicle(db: Session, id: str):
    vehicle = db.query(Vehicle).filter(Vehicle.id == id).first()
    if vehicle:
        db.delete(vehicle)
        db.commit()
