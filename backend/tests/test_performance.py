"""Performance test: verify CP-SAT scales to large n without n! explosion."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _install_mesh(monkeypatch, n_buyers: int, hours: float = 1.0, km: float = 30.0) -> None:
    """Patch OSRM with a complete graph of n_buyers + farm."""
    ids = ["farm"] + [f"buyer-{i}" for i in range(1, n_buyers + 1)]
    graph: dict[tuple[str, str], tuple[float, float]] = {}
    for origin in ids:
        for dest in ids:
            if origin != dest:
                graph[(origin, dest)] = (hours, km)

    def fetch_matrix(points):
        return graph

    def fetch_route(points, consumption, price):
        from app.routing import fuel_cost_rub

        legs = []
        distance = 0.0
        duration = 0.0
        for index in range(len(points) - 1):
            h, k = graph[(points[index][0], points[index + 1][0])]
            distance += k
            duration += h
            legs.append(
                {
                    "from_id": points[index][0],
                    "to_id": points[index + 1][0],
                    "distance_km": k,
                    "hours": h,
                }
            )
        return {
            "distance_km": round(distance, 2),
            "duration_hours": round(duration, 2),
            "fuel_liters": round(distance / 100.0 * consumption, 2),
            "fuel_cost_rub": round(fuel_cost_rub(distance, consumption, price), 2),
            "legs": legs,
            "waypoints": [
                {"id": pid, "longitude": lon, "latitude": lat}
                for pid, lon, lat in points
            ],
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon, lat] for pid, lon, lat in points],
            },
        }

    monkeypatch.setattr("app.planning.fetch_matrix", fetch_matrix)
    monkeypatch.setattr("app.planning.fetch_route", fetch_route)


def test_fifty_buyers_solves_quickly(monkeypatch) -> None:
    """50 buyers should solve in seconds, not hours (old solver would OOM)."""
    _install_mesh(monkeypatch, 50, hours=1.0, km=30.0)

    payload = {
        "farm": {"name": "Хозяйство", "longitude": 36.6, "latitude": 55.1},
        "products": [
            {"id": "berry", "name": "Ягода", "stock_kg": 5000, "max_delivery_hours": 24}
        ],
        "buyers": [
            {
                "id": f"buyer-{i}",
                "name": f"Покупатель {i}",
                "longitude": 36.6 + i * 0.01,
                "latitude": 55.1,
                "orders": [
                    {"product_id": "berry", "demand_kg": 100, "price_per_kg": 10}
                ],
            }
            for i in range(1, 51)
        ],
        "vehicles": [
            {
                "id": f"vehicle-{letter}",
                "name": f"Машина {letter.upper()}",
                "capacity_kg": 500,
                "fuel_consumption_l_per_100km": 10,
                "fuel_price_rub_per_liter": 50,
                "max_trips": 1,
                "max_stops": 5,
                "available": True,
            }
            for letter in ("a", "b", "c", "d", "e")
        ],
    }

    import time

    start = time.time()
    response = client.post("/api/v1/plan", json=payload)
    elapsed = time.time() - start

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("optimal", "feasible")
    assert body["revenue"] > 0
    assert body["profit"] > 0
    # Should solve in under 180 seconds (old solver with n! enumeration would never finish
    # for 50 buyers × 5 vehicles × 3 trips × 5 max_stops — that's ~3000 CP-SAT variables)
    assert elapsed < 180, f"Took {elapsed:.1f}s, expected < 180s"


def test_hundred_buyers_solves_in_reasonable_time(monkeypatch) -> None:
    """100 buyers with max_stops=3 should still finish quickly."""
    _install_mesh(monkeypatch, 100, hours=0.5, km=10.0)

    payload = {
        "farm": {"name": "Хозяйство", "longitude": 36.6, "latitude": 55.1},
        "products": [
            {"id": "berry", "name": "Ягода", "stock_kg": 10000, "max_delivery_hours": 24}
        ],
        "buyers": [
            {
                "id": f"buyer-{i}",
                "name": f"Покупатель {i}",
                "longitude": 36.6 + i * 0.005,
                "latitude": 55.1,
                "orders": [
                    {"product_id": "berry", "demand_kg": 50, "price_per_kg": 10}
                ],
            }
            for i in range(1, 101)
        ],
        "vehicles": [
            {
                "id": f"vehicle-{letter}",
                "name": f"Машина {letter.upper()}",
                "capacity_kg": 300,
                "fuel_consumption_l_per_100km": 10,
                "fuel_price_rub_per_liter": 50,
                "max_trips": 1,
                "max_stops": 3,
                "available": True,
            }
            for letter in ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j")
        ],
    }

    import time

    start = time.time()
    response = client.post("/api/v1/plan", json=payload)
    elapsed = time.time() - start

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("optimal", "feasible")
    assert body["revenue"] > 0
    # Should solve in under 120 seconds
    assert elapsed < 120, f"Took {elapsed:.1f}s, expected < 120s"
