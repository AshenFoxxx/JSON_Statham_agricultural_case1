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
    travel_distance_km: float = Field(
        ge=0,
        description="Километры напрямую от хозяйства. Используются, только если список legs пуст.",
    )
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
    fuel_consumption_l_per_100km: float = Field(gt=0, description="Расход топлива, л/100 км")
    fuel_price_rub_per_liter: float = Field(ge=0, description="Цена топлива, руб/л")
    max_trips: int = Field(ge=1, le=10, description="Сколько выездов машина может сделать")
    max_stops: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Сколько покупателей можно объехать за один выезд",
    )
    available: bool = True


class Leg(BaseModel):
    from_id: str = Field(min_length=1, description="farm или id покупателя")
    to_id: str = Field(min_length=1, description="farm или id покупателя")
    hours: float = Field(ge=0, description="Время перегона, ч")
    distance_km: float = Field(ge=0, description="Длина перегона, км")


class RoutePoint(BaseModel):
    id: str = Field(min_length=1)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)


class RouteRequest(BaseModel):
    points: list[RoutePoint] = Field(min_length=2)
    fuel_consumption_l_per_100km: float = Field(default=35, gt=0)
    fuel_price_rub_per_liter: float = Field(default=62, ge=0)


class RouteLegOut(BaseModel):
    from_id: str
    to_id: str
    distance_km: float = Field(ge=0)
    hours: float = Field(ge=0)


class RouteResponse(BaseModel):
    distance_km: float
    duration_hours: float
    fuel_liters: float
    fuel_cost_rub: float
    legs: list[RouteLegOut]
    waypoints: list[RoutePoint]
    geometry: dict


class PlanRequest(BaseModel):
    products: list[Product] = Field(min_length=1)
    buyers: list[Buyer] = Field(min_length=1)
    vehicles: list[Vehicle] = Field(min_length=1)
    legs: list[Leg] = Field(
        default_factory=list,
        description="Перегоны между хозяйством (farm) и покупателями. Без них рейс везёт одному покупателю.",
    )

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

        if "farm" in buyer_ids:
            raise ValueError("Идентификатор farm зарезервирован для хозяйства")

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

        known_places = set(buyer_ids) | {"farm"}
        seen_legs: set[tuple[str, str]] = set()
        for leg in self.legs:
            if leg.from_id not in known_places or leg.to_id not in known_places:
                raise ValueError(
                    f"Перегон {leg.from_id} -> {leg.to_id} ссылается на неизвестную точку"
                )
            if leg.from_id == leg.to_id:
                raise ValueError(f"Перегон {leg.from_id} ведёт в ту же точку")
            key = (leg.from_id, leg.to_id)
            if key in seen_legs:
                raise ValueError(f"Перегон {leg.from_id} -> {leg.to_id} указан дважды")
            seen_legs.add(key)
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


class Stop(BaseModel):
    buyer_id: str
    arrival_hours: float = Field(ge=0, description="Часы с момента выезда с хозяйства")
    load_kg: float = Field(ge=0, description="Сколько килограммов выгружается здесь")


class Trip(BaseModel):
    vehicle_id: str
    stops: list[Stop] = Field(min_length=1)
    distance_km: float = Field(ge=0, description="Сумма километров перегонов этого выезда")
    cost: float = Field(ge=0, description="Топливо этого выезда, руб")
    load_kg: float = Field(ge=0, description="Суммарная загрузка выезда, кг")


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
