from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from app.routing import fetch_matrix, fetch_route
from app.schemas import PlanRequest, PlanResponse, RoutePoint
from app.solver_cp_sat import FARM, solve_plan


def build_plan(request: PlanRequest) -> PlanResponse:
    """Считает дороги между точками, план поставок и линию каждого выезда."""
    points = [(FARM, request.farm.longitude, request.farm.latitude)]
    buyers = {buyer.id: buyer for buyer in request.buyers}
    points.extend((buyer.id, buyer.longitude, buyer.latitude) for buyer in request.buyers)
    graph = fetch_matrix(points)
    started = perf_counter()
    plan = solve_plan(request, graph, time_limit_seconds=request.time_limit_seconds)
    search_seconds = round(perf_counter() - started, 2)
    vehicles = {vehicle.id: vehicle for vehicle in request.vehicles}

    def route_trip(trip):
        route_points = [(FARM, request.farm.longitude, request.farm.latitude)]
        for stop in trip.stops:
            buyer = buyers[stop.buyer_id]
            route_points.append((buyer.id, buyer.longitude, buyer.latitude))
        route_points.append((FARM, request.farm.longitude, request.farm.latitude))
        vehicle = vehicles[trip.vehicle_id]
        return fetch_route(
            route_points,
            vehicle.fuel_consumption_l_per_100km,
            vehicle.fuel_price_rub_per_liter,
        )

    if plan.trips:
        workers = min(8, len(plan.trips))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            routed_list = list(pool.map(route_trip, plan.trips))
    else:
        routed_list = []

    trips = []
    ready_hours: dict[str, float] = {}
    unload_hours_per_kg = request.unload_seconds_per_kg / 3600.0
    for trip, routed in zip(plan.trips, routed_list):
        elapsed = ready_hours.get(trip.vehicle_id, 0.0)
        stops = []
        for stop, leg in zip(trip.stops, routed["legs"]):
            elapsed += leg["hours"] + unload_hours_per_kg * stop.load_kg
            stops.append(stop.model_copy(update={"arrival_hours": round(elapsed, 2)}))
        if routed["legs"]:
            ready_hours[trip.vehicle_id] = elapsed + routed["legs"][-1]["hours"]
        trips.append(
            trip.model_copy(
                update={
                    "stops": stops,
                    "distance_km": routed["distance_km"],
                    "cost": routed["fuel_cost_rub"],
                    "waypoints": [RoutePoint.model_validate(point) for point in routed["waypoints"]],
                    "geometry": routed["geometry"],
                }
            )
        )

    transport_cost = round(sum(trip.cost for trip in trips), 2)
    return plan.model_copy(
        update={
            "trips": trips,
            "transport_cost": transport_cost,
            "profit": round(plan.revenue - transport_cost, 2),
            "search_seconds": search_seconds,
        }
    )
