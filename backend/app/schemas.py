from enum import Enum

from pydantic import BaseModel, Field, model_validator


class Product(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    stock_kg: float = Field(gt=0, description="Запас на хозяйстве, кг")
    max_delivery_hours: float = Field(
        gt=0,
        description="Предельное время в пути. Срок на складе не учитывается.",
    )


class BuyerOrder(BaseModel):
    product_id: str = Field(min_length=1)
    demand_kg: float = Field(gt=0, description="Максимальный объём заказа, кг")
    price_per_kg: float = Field(ge=0, description="Закупочная цена, руб/кг")


class Buyer(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    travel_time_hours: float = Field(ge=0, description="Время в пути от хозяйства, ч")
    orders: list[BuyerOrder] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_orders(self) -> "Buyer":
        product_ids = [order.product_id for order in self.orders]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError(f"У покупателя {self.id} культура указана дважды")
        return self


class Vehicle(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    capacity_kg: float = Field(gt=0, description="Грузоподъёмность одного рейса, кг")
    cost_per_trip: float = Field(ge=0, description="Стоимость одного рейса, руб")
    max_trips: int = Field(ge=1, le=10, description="Сколько рейсов машина может сделать")
    available: bool = True


class PlanRequest(BaseModel):
    products: list[Product] = Field(min_length=1)
    buyers: list[Buyer] = Field(min_length=1)
    vehicles: list[Vehicle] = Field(min_length=1)

    @model_validator(mode="after")
    def references_exist(self) -> "PlanRequest":
        product_ids = [product.id for product in self.products]
        buyer_ids = [buyer.id for buyer in self.buyers]
        vehicle_ids = [vehicle.id for vehicle in self.vehicles]
        for label, ids in (
            ("культур", product_ids),
            ("покупателей", buyer_ids),
            ("машин", vehicle_ids),
        ):
            if len(ids) != len(set(ids)):
                raise ValueError(f"Идентификаторы {label} должны быть уникальными")

        known_products = set(product_ids)
        for buyer in self.buyers:
            unknown = [
                order.product_id
                for order in buyer.orders
                if order.product_id not in known_products
            ]
            if unknown:
                raise ValueError(
                    f"У покупателя {buyer.id} неизвестные культуры: {', '.join(unknown)}"
                )
        return self


class SolverStatus(str, Enum):
    NOT_SOLVED = "not_solved"
    OPTIMAL = "optimal"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"


class Shipment(BaseModel):
    product_id: str
    buyer_id: str
    vehicle_id: str
    quantity_kg: float = Field(ge=0)


class Trip(BaseModel):
    vehicle_id: str
    buyer_id: str
    cost: float = Field(ge=0)
    load_kg: float = Field(ge=0)


class ProductBalance(BaseModel):
    product_id: str
    stock_kg: float
    shipped_kg: float
    leftover_kg: float = Field(description="Запас минус отгружено")
    loss_kg: float = Field(
        description="Часть остатка, которую нельзя доставить ни одному покупателю в срок"
    )


class PlanResponse(BaseModel):
    status: SolverStatus
    objective: str = Field(description="Целевая функция. Сейчас это максимум прибыли.")
    message: str
    assumptions: list[str]
    shipments: list[Shipment]
    trips: list[Trip]
    revenue: float = Field(description="Сумма quantity_kg * price_per_kg по отгрузкам, руб")
    transport_cost: float = Field(description="Сумма стоимости выполненных рейсов, руб")
    profit: float = Field(description="Выручка минус транспортные затраты, руб")
    balances: list[ProductBalance]
