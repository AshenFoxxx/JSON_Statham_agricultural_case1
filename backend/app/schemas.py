from enum import Enum

from pydantic import BaseModel, Field, model_validator


class Product(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    stock_kg: float = Field(gt=0, description="Запас на хозяйстве, кг")
    max_delivery_hours: float = Field(
        gt=0,
        description="Срок с начала смены до конца разгрузки у покупателя, ч.",
    )


class BuyerOrder(BaseModel):
    product_id: str = Field(min_length=1)
    demand_kg: float = Field(gt=0, description="Максимальный объём заказа, кг")
    price_per_kg: float = Field(ge=0, description="Закупочная цена, руб/кг")


class Farm(BaseModel):
    name: str = Field(min_length=1)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)


class Buyer(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)
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
    max_trips: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Сколько выездов машина может сделать за план. Следующий стартует после возврата.",
    )
    max_stops: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Сколько покупателей можно объехать за один выезд",
    )
    available: bool = True


class RoutePoint(BaseModel):
    id: str = Field(min_length=1)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)


class MatrixBuyer(BaseModel):
    id: str = Field(min_length=1)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)


class MatrixPrefetchRequest(BaseModel):
    farm: Farm
    buyers: list[MatrixBuyer] = Field(min_length=1)


class MatrixPrefetchResponse(BaseModel):
    ok: bool = True
    points: int


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
    farm: Farm
    products: list[Product] = Field(min_length=1)
    buyers: list[Buyer] = Field(min_length=1)
    vehicles: list[Vehicle] = Field(min_length=1)
    unload_seconds_per_kg: float = Field(
        default=0,
        ge=0,
        description="Секунды разгрузки на килограмм. 0 — мгновенно. Погрузка на хозяйстве в срок не входит.",
    )
    time_limit_seconds: float = Field(
        default=25,
        ge=5,
        le=600,
        description="Лимит поиска CP-SAT, секунды (5–600). По истечении — лучший найденный план (status feasible), не обязательно доказанный оптимум.",
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
    arrival_hours: float = Field(
        ge=0,
        description="Часы с начала смены до конца разгрузки на этой остановке",
    )
    load_kg: float = Field(ge=0, description="Сколько килограммов выгружается здесь")


class Trip(BaseModel):
    vehicle_id: str
    stops: list[Stop] = Field(min_length=1)
    distance_km: float = Field(ge=0, description="Длина маршрута по дорогам, км")
    cost: float = Field(ge=0, description="Топливо этого выезда, руб")
    load_kg: float = Field(ge=0, description="Суммарная загрузка выезда, кг")
    waypoints: list[RoutePoint] = Field(
        default_factory=list,
        description="Точки по порядку, первая — хозяйство",
    )
    geometry: dict = Field(
        default_factory=dict,
        description="GeoJSON LineString дороги этого выезда",
    )


class ProductBalance(BaseModel):
    product_id: str
    stock_kg: float
    shipped_kg: float
    leftover_kg: float = Field(description="Запас минус отгружено")
    loss_kg: float = Field(
        description="Равно leftover_kg: невывезенное в этом плане считается порчей"
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
    search_seconds: float = Field(
        default=0,
        ge=0,
        description="Стены часов на сбор модели и поиск CP-SAT, без OSRM",
    )
