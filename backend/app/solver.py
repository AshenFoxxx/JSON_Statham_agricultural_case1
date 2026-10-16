from collections import defaultdict

import pulp

from app.demo_data import ASSUMPTIONS
from app.schemas import (
    PlanRequest,
    PlanResponse,
    ProductBalance,
    Shipment,
    SolverStatus,
    Trip,
)

OBJECTIVE = "maximize_profit"
LOAD_EPS = 1e-3


def solve_plan(request: PlanRequest) -> PlanResponse:
    """Строит план максимума прибыли по культурам, заказам и машинам из запроса."""
    orders = {
        (buyer.id, order.product_id): order
        for buyer in request.buyers
        for order in buyer.orders
    }
    products = list(request.products)
    buyers = list(request.buyers)
    vehicles = [vehicle for vehicle in request.vehicles if vehicle.available]

    def can_ship(buyer_index: int, product_index: int) -> bool:
        buyer = buyers[buyer_index]
        product = products[product_index]
        return (
            buyer.travel_time_hours <= product.max_delivery_hours
            and (buyer.id, product.id) in orders
        )

    quantity: dict[tuple[int, int, int, int], pulp.LpVariable] = {}
    assign: dict[tuple[int, int, int], pulp.LpVariable] = {}
    problem = pulp.LpProblem("plan", pulp.LpMaximize)

    for vehicle_index, vehicle in enumerate(vehicles):
        for trip_index in range(vehicle.max_trips):
            for buyer_index in range(len(buyers)):
                assign[vehicle_index, trip_index, buyer_index] = pulp.LpVariable(
                    f"a_{vehicle_index}_{trip_index}_{buyer_index}",
                    cat="Binary",
                )
                for product_index in range(len(products)):
                    if not can_ship(buyer_index, product_index):
                        continue
                    quantity[vehicle_index, trip_index, buyer_index, product_index] = pulp.LpVariable(
                        f"q_{vehicle_index}_{trip_index}_{buyer_index}_{product_index}",
                        lowBound=0,
                    )

    if not quantity:
        return _response(
            request,
            SolverStatus.OPTIMAL,
            "По этим данным отгружать нечего: нет доступных машин или ни одна культура не успевает до покупателей.",
            [],
            [],
        )

    for vehicle_index, vehicle in enumerate(vehicles):
        for trip_index in range(vehicle.max_trips):
            problem += (
                pulp.lpSum(
                    assign[vehicle_index, trip_index, buyer_index]
                    for buyer_index in range(len(buyers))
                )
                <= 1,
                f"one_buyer_{vehicle_index}_{trip_index}",
            )
            for buyer_index in range(len(buyers)):
                loaded = [
                    quantity[vehicle_index, trip_index, buyer_index, product_index]
                    for product_index in range(len(products))
                    if (vehicle_index, trip_index, buyer_index, product_index) in quantity
                ]
                flag = assign[vehicle_index, trip_index, buyer_index]
                if not loaded:
                    problem += flag == 0, f"no_cargo_{vehicle_index}_{trip_index}_{buyer_index}"
                    continue
                problem += (
                    pulp.lpSum(loaded) <= vehicle.capacity_kg * flag,
                    f"capacity_{vehicle_index}_{trip_index}_{buyer_index}",
                )
                problem += (
                    pulp.lpSum(loaded) >= LOAD_EPS * flag,
                    f"no_empty_{vehicle_index}_{trip_index}_{buyer_index}",
                )

    for product_index, product in enumerate(products):
        loaded = [var for key, var in quantity.items() if key[3] == product_index]
        problem += pulp.lpSum(loaded) <= product.stock_kg, f"stock_{product_index}"

    for buyer_index, buyer in enumerate(buyers):
        for product_index, product in enumerate(products):
            order = orders.get((buyer.id, product.id))
            if order is None:
                continue
            loaded = [
                var
                for key, var in quantity.items()
                if key[2] == buyer_index and key[3] == product_index
            ]
            problem += pulp.lpSum(loaded) <= order.demand_kg, f"demand_{buyer_index}_{product_index}"

    revenue_expr = []
    for (vehicle_index, trip_index, buyer_index, product_index), var in quantity.items():
        price = orders[(buyers[buyer_index].id, products[product_index].id)].price_per_kg
        revenue_expr.append(price * var)
    cost_expr = [
        vehicle.cost_per_trip * assign[vehicle_index, trip_index, buyer_index]
        for vehicle_index, vehicle in enumerate(vehicles)
        for trip_index in range(vehicle.max_trips)
        for buyer_index in range(len(buyers))
    ]
    problem += pulp.lpSum(revenue_expr) - pulp.lpSum(cost_expr)

    status_code = problem.solve(pulp.PULP_CBC_CMD(msg=False))
    status_name = pulp.LpStatus.get(status_code, "Not Solved")
    if status_name == "Infeasible":
        return _response(
            request,
            SolverStatus.INFEASIBLE,
            "Для этих данных нет допустимого плана.",
            [],
            [],
        )
    if status_name != "Optimal":
        return _response(
            request,
            SolverStatus.NOT_SOLVED,
            "Решатель не нашёл план. Проверьте входные данные и повторите запрос.",
            [],
            [],
        )

    shipment_kg: dict[tuple[str, str, str], float] = defaultdict(float)
    trips: list[Trip] = []
    for vehicle_index, vehicle in enumerate(vehicles):
        for trip_index in range(vehicle.max_trips):
            for buyer_index, buyer in enumerate(buyers):
                if _value(assign[vehicle_index, trip_index, buyer_index]) < 0.5:
                    continue
                load = 0.0
                for product_index, product in enumerate(products):
                    var = quantity.get((vehicle_index, trip_index, buyer_index, product_index))
                    if var is None:
                        continue
                    amount = _value(var)
                    if amount < LOAD_EPS:
                        continue
                    shipment_kg[(product.id, buyer.id, vehicle.id)] += amount
                    load += amount
                if load < LOAD_EPS:
                    continue
                trips.append(
                    Trip(
                        vehicle_id=vehicle.id,
                        buyer_id=buyer.id,
                        cost=round(vehicle.cost_per_trip, 2),
                        load_kg=round(load, 3),
                    )
                )

    shipments = [
        Shipment(
            product_id=product_id,
            buyer_id=buyer_id,
            vehicle_id=vehicle_id,
            quantity_kg=round(amount, 3),
        )
        for (product_id, buyer_id, vehicle_id), amount in sorted(shipment_kg.items())
        if amount >= LOAD_EPS
    ]
    return _response(
        request,
        SolverStatus.OPTIMAL,
        "План рассчитан по данным запроса.",
        shipments,
        trips,
    )


def _response(
    request: PlanRequest,
    status: SolverStatus,
    message: str,
    shipments: list[Shipment],
    trips: list[Trip],
) -> PlanResponse:
    orders = {
        (buyer.id, order.product_id): order
        for buyer in request.buyers
        for order in buyer.orders
    }
    revenue = 0.0
    shipped_by_product: dict[str, float] = defaultdict(float)
    for shipment in shipments:
        price = orders[(shipment.buyer_id, shipment.product_id)].price_per_kg
        revenue += shipment.quantity_kg * price
        shipped_by_product[shipment.product_id] += shipment.quantity_kg
    transport_cost = sum(trip.cost for trip in trips)
    balances = []
    for product in request.products:
        eligible_demand = sum(
            order.demand_kg
            for buyer in request.buyers
            if buyer.travel_time_hours <= product.max_delivery_hours
            for order in buyer.orders
            if order.product_id == product.id
        )
        shipped = shipped_by_product[product.id]
        balances.append(
            ProductBalance(
                product_id=product.id,
                stock_kg=product.stock_kg,
                shipped_kg=round(shipped, 3),
                leftover_kg=round(product.stock_kg - shipped, 3),
                loss_kg=round(max(0.0, product.stock_kg - eligible_demand), 3),
            )
        )
    return PlanResponse(
        status=status,
        objective=OBJECTIVE,
        message=message,
        assumptions=ASSUMPTIONS,
        shipments=shipments,
        trips=trips,
        revenue=round(revenue, 2),
        transport_cost=round(transport_cost, 2),
        profit=round(revenue - transport_cost, 2),
        balances=balances,
    )


def _value(var: pulp.LpVariable) -> float:
    raw = pulp.value(var)
    if raw is None:
        return 0.0
    return float(raw)
