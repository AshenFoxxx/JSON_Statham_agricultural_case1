from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(String, primary_key=True, default="farm")
    name = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

    products = relationship("Product", back_populates="farm")


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    stock_kg = Column(Float, nullable=False)
    max_delivery_hours = Column(Float, nullable=False)
    farm_id = Column(String, ForeignKey("farms.id"))

    farm = relationship("Farm", back_populates="products")
    orders = relationship("BuyerOrder", back_populates="product")


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

    orders = relationship("BuyerOrder", back_populates="buyer")


class BuyerOrder(Base):
    __tablename__ = "buyer_orders"

    id = Column(String, primary_key=True, default=lambda: f"order-{id}")
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    buyer_id = Column(String, ForeignKey("buyers.id"), nullable=False)
    demand_kg = Column(Float, nullable=False)
    price_per_kg = Column(Float, nullable=False)

    product = relationship("Product", back_populates="orders")
    buyer = relationship("Buyer", back_populates="orders")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    capacity_kg = Column(Float, nullable=False)
    fuel_consumption_l_per_100km = Column(Float, nullable=False)
    fuel_price_rub_per_liter = Column(Float, nullable=False)
    max_trips = Column(Integer, nullable=False)
    max_stops = Column(Integer, nullable=False)
    available = Column(Boolean, default=True)
