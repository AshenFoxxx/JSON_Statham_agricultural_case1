from collections import defaultdict
from dataclasses import dataclass

import pulp

from app.demo_data import ASSUMPTIONS
from app.routing import fuel_cost_rub
from app.schemas import (
    PlanRequest,
    PlanResponse,
    ProductBalance,
    Shipment,
    SolverStatus,
    Stop,
    Trip,
)

OBJECTIVE = "maximize_profit"
LOAD_EPS = 1e-3
FARM = "farm"


@dataclass
class Route:
    stops: tuple[str, ...]
    arrival: dict[str, float]
    distance_km: float


def solve_plan(request: PlanRequest) -> PlanResponse:
    """Строит план максимума прибыли. Один выезд может объехать нескольких покупателей."""
    orders = {
        (buyer.id, order.product_id): order
        for buyer in request.buyers
        for order in buyer.orders
    }
    products = list(request.products)
    buyers = list(request.buyers)
    buyer_ids = [buyer.id for buyer in buyers]
    vehicles = [vehicle for vehicle in request.vehicles if vehicle.available]
    graph = build_graph(request)
    stop_limit = max((vehicle.max_stops for vehicle in request.vehicles), default=1)
    all_routes = enumerate_routes(buyer_ids, graph, stop_limit)
    arrivals = earliest_arrivals(all_routes)

    if not vehicles or not all_routes:
        return _response(
            request,
            SolverStatus.OPTIMAL,
            "По этим данным отгружать нечего: нет доступных машин или ни одна культура не успевает до покупателей.",
            [],
            [],
            arrivals,
        )

    quantity: dict[tuple[int, int, int, int, int], pulp.LpVariable] = {}
    assign: dict[tuple[int, int, int], pulp.LpVariable] = {}
    problem = pulp.LpProblem("plan", pulp.LpMaximize)

    for vehicle_index, vehicle in enumerate(vehicles):
        vehicle_routes = [route for route in all_routes if len(route.stops) <= vehicle.max_stops]
        for trip_index in range(vehicle.max_trips):
            for route_index, route in enumerate(vehicle_routes):
                assign[vehicle_index, trip_index, route_index] = pulp.LpVariable(
                    f"a_{vehicle_index}_{trip_index}_{route_index}",
                    cat="Binary",
                )
                for stop_index, buyer_id in enumerate(route.stops):
                    buyer_index = buyer_ids.index(buyer_id)
                    arrived = route.arrival[buyer_id]
                    for product_index, product in enumerate(products):
                        if arrived > product.max_delivery_hours:
                            continue
                        if (buyer_id, product.id) not in orders:
                            continue
                        quantity[
                            vehicle_index, trip_index, route_index, stop_index, product_index
                        ] = pulp.LpVariable(
                            f"q_{vehicle_index}_{trip_index}_{route_index}_{stop_index}_{product_index}",
                            lowBound=0,
                        )

    if not quantity:
        return _response(
            request,
            SolverStatus.OPTIMAL,
            "По этим данным отгружать нечего: нет доступных машин или ни одна культура не успевает до покупателей.",
            [],
            [],
            arrivals,
        )

    for vehicle_index, vehicle in enumerate(vehicles):
        vehicle_routes = [route for route in all_routes if len(route.stops) <= vehicle.max_stops]
        for trip_index in range(vehicle.max_trips):
            chosen = [
                assign[vehicle_index, trip_index, route_index]
                for route_index in range(len(vehicle_routes))
                if (vehicle_index, trip_index, route_index) in assign
            ]
            if chosen:
                problem += pulp.lpSum(chosen) <= 1, f"one_route_{vehicle_index}_{trip_index}"
            for route_index in range(len(vehicle_routes)):
                flag = assign.get((vehicle_index, trip_index, route_index))
                if flag is None:
                    continue
                loaded = [
                    var
                    for key, var in quantity.items()
                    if key[0] == vehicle_index and key[1] == trip_index and key[2] == route_index
                ]
                if not loaded:
                    problem += flag == 0, f"no_cargo_{vehicle_index}_{trip_index}_{route_index}"
                    continue
                problem += (
                    pulp.lpSum(loaded) <= vehicle.capacity_kg * flag,
                    f"capacity_{vehicle_index}_{trip_index}_{route_index}",
                )
                problem += (
                    pulp.lpSum(loaded) >= LOAD_EPS * flag,
                    f"no_empty_{vehicle_index}_{trip_index}_{route_index}",
                )

    for product_index, product in enumerate(products):
        loaded = [var for key, var in quantity.items() if key[4] == product_index]
        problem += pulp.lpSum(loaded) <= product.stock_kg, f"stock_{product_index}"

    for buyer_index, buyer in enumerate(buyers):
        for product_index, product in enumerate(products):
            if (buyer.id, product.id) not in orders:
                continue
            loaded = []
            for key, var in quantity.items():
                vehicle_routes = [
                    route
                    for route in all_routes
                    if len(route.stops) <= vehicles[key[0]].max_stops
                ]
                buyer_id = vehicle_routes[key[2]].stops[key[3]]
                if buyer_id == buyer.id and key[4] == product_index:
                    loaded.append(var)
            demand = orders[(buyer.id, product.id)].demand_kg
            problem += pulp.lpSum(loaded) <= demand, f"demand_{buyer_index}_{product_index}"

    revenue_expr = []
    for key, var in quantity.items():
        vehicle_routes = [
            route for route in all_routes if len(route.stops) <= vehicles[key[0]].max_stops
        ]
        buyer_id = vehicle_routes[key[2]].stops[key[3]]
        price = orders[(buyer_id, products[key[4]].id)].price_per_kg
        revenue_expr.append(price * var)
    cost_expr = []
    for (vehicle_index, _trip_index, route_index), flag in assign.items():
        vehicle = vehicles[vehicle_index]
        vehicle_routes = [route for route in all_routes if len(route.stops) <= vehicle.max_stops]
        route = vehicle_routes[route_index]
        cost_expr.append(
            fuel_cost_rub(
                route.distance_km,
                vehicle.fuel_consumption_l_per_100km,
                vehicle.fuel_price_rub_per_liter,
            )
            * flag
        )
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
            arrivals,
        )
    if status_name != "Optimal":
        return _response(
            request,
            SolverStatus.NOT_SOLVED,
            "Решатель не нашёл план. Проверьте входные данные и повторите запрос.",
            [],
            [],
            arrivals,
        )

    shipment_kg: dict[tuple[str, str, str], float] = defaultdict(float)
    trips: list[Trip] = []
    for vehicle_index, vehicle in enumerate(vehicles):
        vehicle_routes = [route for route in all_routes if len(route.stops) <= vehicle.max_stops]
        for trip_index in range(vehicle.max_trips):
            for route_index, route in enumerate(vehicle_routes):
                flag = assign.get((vehicle_index, trip_index, route_index))
                if flag is None or _value(flag) < 0.5:
                    continue
                stops: list[Stop] = []
                total_load = 0.0
                for stop_index, buyer_id in enumerate(route.stops):
                    stop_load = 0.0
                    for product_index, product in enumerate(products):
                        var = quantity.get(
                            (vehicle_index, trip_index, route_index, stop_index, product_index)
                        )
                        if var is None:
                            continue
                        amount = _value(var)
                        if amount < LOAD_EPS:
                            continue
                        shipment_kg[(product.id, buyer_id, vehicle.id)] += amount
                        stop_load += amount
                    total_load += stop_load
                    stops.append(
                        Stop(
                            buyer_id=buyer_id,
                            arrival_hours=round(route.arrival[buyer_id], 2),
                            load_kg=round(stop_load, 3),
                        )
                    )
                if total_load < LOAD_EPS:
                    continue
                trips.append(
                    Trip(
                        vehicle_id=vehicle.id,
                        stops=stops,
                        distance_km=round(route.distance_km, 2),
                        cost=round(
                            fuel_cost_rub(
                                route.distance_km,
                                vehicle.fuel_consumption_l_per_100km,
                                vehicle.fuel_price_rub_per_liter,
                            ),
                            2,
                        ),
                        load_kg=round(total_load, 3),
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
        arrivals,
    )


def build_graph(request: PlanRequest) -> dict[tuple[str, str], tuple[float, float]]:
    """Перегон: (часы, километры). Без legs берётся прямая дорога от хозяйства."""
    if request.legs:
        return {
            (leg.from_id, leg.to_id): (leg.hours, leg.distance_km) for leg in request.legs
        }
    return {
        (FARM, buyer.id): (buyer.travel_time_hours, buyer.travel_distance_km)
        for buyer in request.buyers
    }


def enumerate_routes(
    buyer_ids: list[str],
    graph: dict[tuple[str, str], tuple[float, float]],
    max_stops: int,
) -> list[Route]:
    found: list[Route] = []

    def walk(path: list[str], arrival: dict[str, float], distance_km: float) -> None:
        if path:
            found.append(Route(tuple(path), dict(arrival), distance_km))
        if len(path) >= max_stops:
            return
        last = path[-1] if path else FARM
        elapsed = arrival[last] if path else 0.0
        for buyer_id in buyer_ids:
            if buyer_id in arrival:
                continue
            hop = graph.get((last, buyer_id))
            if hop is None:
                continue
            hop_hours, hop_km = hop
            path.append(buyer_id)
            arrival[buyer_id] = elapsed + hop_hours
            walk(path, arrival, distance_km + hop_km)
            path.pop()
            del arrival[buyer_id]

    if max_stops >= 1:
        walk([], {}, 0.0)
    return found


def earliest_arrivals(routes: list[Route]) -> dict[str, float]:
    best: dict[str, float] = {}
    for route in routes:
        for buyer_id, hours in route.arrival.items():
            current = best.get(buyer_id)
            if current is None or hours < current:
                best[buyer_id] = hours
    return best


def _response(
    request: PlanRequest,
    status: SolverStatus,
    message: str,
    shipments: list[Shipment],
    trips: list[Trip],
    arrivals: dict[str, float],
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
        eligible_demand = 0.0
        for buyer in request.buyers:
            order = orders.get((buyer.id, product.id))
            arrived = arrivals.get(buyer.id)
            if order is None or arrived is None or arrived > product.max_delivery_hours:
                continue
            eligible_demand += order.demand_kg
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
