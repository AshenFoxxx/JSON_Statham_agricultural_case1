"""Граница optimal / feasible при лимите поиска 120 с. Дороги — полная сетка, без OSRM."""

import time

from app.schemas import PlanRequest, SolverStatus
from app.solver_cp_sat import FARM, solve_plan


def _mesh(ids: list[str], hours: float = 1.0, km: float = 30.0) -> dict[tuple[str, str], tuple[float, float]]:
    return {
        (origin, dest): (hours, km)
        for origin in ids
        for dest in ids
        if origin != dest
    }


def _request(n_buyers: int, n_vehicles: int, max_stops: int = 3, max_trips: int = 1) -> PlanRequest:
    stock = n_buyers * 100
    return PlanRequest.model_validate(
        {
            "farm": {"name": "Хозяйство", "longitude": 36.6, "latitude": 55.1},
            "products": [
                {
                    "id": "berry",
                    "name": "Ягода",
                    "stock_kg": stock,
                    "max_delivery_hours": 24,
                }
            ],
            "buyers": [
                {
                    "id": f"buyer-{index}",
                    "name": f"Покупатель {index}",
                    "longitude": 36.6 + index * 0.01,
                    "latitude": 55.1,
                    "orders": [
                        {"product_id": "berry", "demand_kg": 100, "price_per_kg": 10}
                    ],
                }
                for index in range(1, n_buyers + 1)
            ],
            "vehicles": [
                {
                    "id": f"vehicle-{index}",
                    "name": f"Машина {index}",
                    "capacity_kg": 200,
                    "fuel_consumption_l_per_100km": 10,
                    "fuel_price_rub_per_liter": 50,
                    "max_trips": max_trips,
                    "max_stops": max_stops,
                    "available": True,
                }
                for index in range(1, n_vehicles + 1)
            ],
        }
    )


def solve_mesh(
    n_buyers: int,
    n_vehicles: int,
    max_stops: int = 3,
    max_trips: int = 1,
    time_limit_seconds: float = 120,
):
    request = _request(n_buyers, n_vehicles, max_stops, max_trips)
    ids = [FARM] + [buyer.id for buyer in request.buyers]
    started = time.perf_counter()
    plan = solve_plan(request, _mesh(ids), time_limit_seconds=time_limit_seconds)
    elapsed = time.perf_counter() - started
    return plan, elapsed


def test_five_buyers_three_vehicles_is_optimal() -> None:
    plan, elapsed = solve_mesh(5, 3, time_limit_seconds=30)
    assert plan.status == SolverStatus.OPTIMAL
    assert elapsed < 30
    assert plan.trips
    for trip in plan.trips:
        assert trip.waypoints[0].id == "farm"
        assert trip.waypoints[-1].id == "farm"
        assert [stop.buyer_id for stop in trip.stops] == [
            point.id for point in trip.waypoints[1:-1]
        ]


def test_ten_buyers_three_vehicles_returns_a_plan() -> None:
    """10 покупателей — край: то оптимум за ~16 с, то feasible на лимите."""
    plan, elapsed = solve_mesh(10, 3, time_limit_seconds=40)
    assert plan.status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
    assert elapsed < 45
    assert plan.trips
    assert plan.profit > 0


def test_fifteen_buyers_three_vehicles_is_feasible_at_minute() -> None:
    """С 15 покупателями за 60 с есть план; после Circuit часто уже оптимум."""
    plan, elapsed = solve_mesh(15, 3, time_limit_seconds=60)
    assert plan.status in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE)
    assert elapsed < 75
    assert plan.trips
    assert plan.profit > 0
