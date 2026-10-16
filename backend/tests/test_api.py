from fastapi.testclient import TestClient

from app.main import app
from app.routing import fuel_cost_rub

client = TestClient(app)


def _payload() -> dict:
    return {
        "farm": {"name": "Хозяйство", "longitude": 36.6, "latitude": 55.1},
        "products": [
            {"id": "berry", "name": "Ягода", "stock_kg": 100, "max_delivery_hours": 5},
            {"id": "apple", "name": "Яблоко", "stock_kg": 100, "max_delivery_hours": 20},
        ],
        "buyers": [
            {
                "id": "near",
                "name": "Ближний",
                "longitude": 36.7,
                "latitude": 55.2,
                "orders": [
                    {"product_id": "berry", "demand_kg": 100, "price_per_kg": 10},
                    {"product_id": "apple", "demand_kg": 50, "price_per_kg": 1},
                ],
            },
            {
                "id": "far",
                "name": "Дальний",
                "longitude": 37.6,
                "latitude": 55.7,
                "orders": [
                    {"product_id": "berry", "demand_kg": 100, "price_per_kg": 100},
                    {"product_id": "apple", "demand_kg": 100, "price_per_kg": 8},
                ],
            },
        ],
        "vehicles": [
            {
                "id": "truck",
                "name": "Газель",
                "capacity_kg": 100,
                "fuel_consumption_l_per_100km": 10,
                "fuel_price_rub_per_liter": 50,
                "max_trips": 1,
                "available": True,
            }
        ],
    }


def install_roads(monkeypatch, hops: dict[tuple[str, str], tuple[float, float]]) -> None:
    """Подменяет OSRM: часы и километры заданы заранее, линия строится по точкам."""

    def fetch_matrix(points):
        return dict(hops)

    def fetch_route(points, consumption, price):
        legs = []
        distance = 0.0
        duration = 0.0
        for index in range(len(points) - 1):
            hours, km = hops[(points[index][0], points[index + 1][0])]
            distance += km
            duration += hours
            legs.append(
                {
                    "from_id": points[index][0],
                    "to_id": points[index + 1][0],
                    "distance_km": km,
                    "hours": hours,
                }
            )
        return {
            "distance_km": round(distance, 2),
            "duration_hours": round(duration, 2),
            "fuel_liters": round(distance / 100.0 * consumption, 2),
            "fuel_cost_rub": round(fuel_cost_rub(distance, consumption, price), 2),
            "legs": legs,
            "waypoints": [
                {"id": point_id, "longitude": lon, "latitude": lat}
                for point_id, lon, lat in points
            ],
            "geometry": {
                "type": "LineString",
                "coordinates": [[lon, lat] for _point_id, lon, lat in points],
            },
        }

    monkeypatch.setattr("app.planning.fetch_matrix", fetch_matrix)
    monkeypatch.setattr("app.planning.fetch_route", fetch_route)


def _mesh(ids: list[str], hours: float = 1.0, km: float = 30.0) -> dict[tuple[str, str], tuple[float, float]]:
    return {
        (origin, dest): (hours, km)
        for origin in ids
        for dest in ids
        if origin != dest
    }


def test_plan_uses_request_prices(monkeypatch) -> None:
    install_roads(
        monkeypatch,
        {
            ("farm", "near"): (2.0, 10.0),
            ("farm", "far"): (10.0, 100.0),
            ("near", "far"): (8.0, 90.0),
            ("far", "near"): (8.0, 90.0),
        },
    )
    cheap = client.post("/api/v1/plan", json=_payload())
    assert cheap.status_code == 200
    cheap_body = cheap.json()
    assert cheap_body["status"] == "optimal"
    assert cheap_body["shipments"] == [
        {
            "product_id": "berry",
            "buyer_id": "near",
            "vehicle_id": "truck",
            "quantity_kg": 100,
        }
    ]
    assert cheap_body["revenue"] == 1000
    assert cheap_body["transport_cost"] == 50
    assert cheap_body["profit"] == 950
    trip = cheap_body["trips"][0]
    assert trip["waypoints"][0]["id"] == "farm"
    assert trip["geometry"]["type"] == "LineString"
    assert trip["geometry"]["coordinates"][0] == [36.6, 55.1]

    expensive = _payload()
    expensive["buyers"][1]["orders"][1]["price_per_kg"] = 20
    costly = client.post("/api/v1/plan", json=expensive)
    assert costly.status_code == 200
    assert costly.json()["shipments"] == [
        {
            "product_id": "apple",
            "buyer_id": "far",
            "vehicle_id": "truck",
            "quantity_kg": 100,
        }
    ]
    assert costly.json()["transport_cost"] == 500
    assert costly.json()["profit"] == 1500


def test_plan_respects_stock_demand_capacity_and_time(monkeypatch) -> None:
    request = client.get("/api/v1/demo").json()
    ids = ["farm"] + [buyer["id"] for buyer in request["buyers"]]
    install_roads(monkeypatch, _mesh(ids))
    response = client.post("/api/v1/plan", json=request)
    assert response.status_code == 200
    body = response.json()
    products = {item["id"]: item for item in request["products"]}
    vehicles = {item["id"]: item for item in request["vehicles"]}
    orders = {
        (buyer["id"], order["product_id"]): order
        for buyer in request["buyers"]
        for order in buyer["orders"]
    }

    arrivals = {
        (trip["vehicle_id"], stop["buyer_id"]): stop["arrival_hours"]
        for trip in body["trips"]
        for stop in trip["stops"]
    }
    shipped_product: dict[str, float] = {}
    shipped_order: dict[tuple[str, str], float] = {}
    for shipment in body["shipments"]:
        product = products[shipment["product_id"]]
        arrival = arrivals[(shipment["vehicle_id"], shipment["buyer_id"])]
        assert arrival <= product["max_delivery_hours"]
        shipped_product[shipment["product_id"]] = (
            shipped_product.get(shipment["product_id"], 0) + shipment["quantity_kg"]
        )
        key = (shipment["buyer_id"], shipment["product_id"])
        shipped_order[key] = shipped_order.get(key, 0) + shipment["quantity_kg"]

    for product_id, amount in shipped_product.items():
        assert amount <= products[product_id]["stock_kg"] + 1e-6
    for key, amount in shipped_order.items():
        assert amount <= orders[key]["demand_kg"] + 1e-6
    for trip in body["trips"]:
        assert trip["load_kg"] <= vehicles[trip["vehicle_id"]]["capacity_kg"] + 1e-6
        assert len(trip["stops"]) <= vehicles[trip["vehicle_id"]]["max_stops"]
        assert abs(sum(stop["load_kg"] for stop in trip["stops"]) - trip["load_kg"]) < 1e-6
        assert trip["waypoints"][0]["id"] == "farm"
        assert [point["id"] for point in trip["waypoints"][1:]] == [
            stop["buyer_id"] for stop in trip["stops"]
        ]
        assert trip["geometry"]["type"] == "LineString"
        vehicle = vehicles[trip["vehicle_id"]]
        expected_cost = (
            trip["distance_km"]
            / 100
            * vehicle["fuel_consumption_l_per_100km"]
            * vehicle["fuel_price_rub_per_liter"]
        )
        assert abs(trip["cost"] - round(expected_cost, 2)) < 0.02
    assert body["profit"] == round(body["revenue"] - body["transport_cost"], 2)


def test_unavailable_vehicle_is_not_used(monkeypatch) -> None:
    install_roads(monkeypatch, {("farm", "near"): (2.0, 10.0), ("farm", "far"): (10.0, 100.0)})
    payload = _payload()
    payload["vehicles"][0]["available"] = False
    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["shipments"] == []
    assert body["trips"] == []
    assert body["profit"] == 0
    balances = {item["product_id"]: item for item in body["balances"]}
    assert balances["berry"]["leftover_kg"] == 100


def test_one_trip_serves_two_buyers(monkeypatch) -> None:
    install_roads(
        monkeypatch,
        {
            ("farm", "near"): (1.0, 10.0),
            ("near", "next"): (1.0, 10.0),
            ("farm", "next"): (4.0, 40.0),
            ("next", "near"): (1.0, 10.0),
        },
    )
    payload = _payload()
    payload["products"] = [
        {"id": "berry", "name": "Ягода", "stock_kg": 80, "max_delivery_hours": 5}
    ]
    payload["buyers"] = [
        {
            "id": "near",
            "name": "Ближний",
            "longitude": 36.7,
            "latitude": 55.2,
            "orders": [{"product_id": "berry", "demand_kg": 40, "price_per_kg": 10}],
        },
        {
            "id": "next",
            "name": "Следующий",
            "longitude": 36.8,
            "latitude": 55.3,
            "orders": [{"product_id": "berry", "demand_kg": 40, "price_per_kg": 10}],
        },
    ]
    payload["vehicles"][0]["capacity_kg"] = 100
    payload["vehicles"][0]["max_stops"] = 2
    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["profit"] == 700
    assert len(body["trips"]) == 1
    assert [stop["buyer_id"] for stop in body["trips"][0]["stops"]] == ["near", "next"]
    assert body["trips"][0]["distance_km"] == 20
    assert body["trips"][0]["cost"] == 100
    assert [point["id"] for point in body["trips"][0]["waypoints"]] == ["farm", "near", "next"]
    assert sorted(item["buyer_id"] for item in body["shipments"]) == ["near", "next"]


def test_extra_kilometers_drop_unprofitable_stop(monkeypatch) -> None:
    install_roads(
        monkeypatch,
        {
            ("farm", "near"): (1.0, 10.0),
            ("near", "next"): (1.0, 200.0),
            ("farm", "next"): (4.0, 210.0),
            ("next", "near"): (1.0, 200.0),
        },
    )
    payload = _payload()
    payload["products"] = [
        {"id": "berry", "name": "Ягода", "stock_kg": 80, "max_delivery_hours": 5}
    ]
    payload["buyers"] = [
        {
            "id": "near",
            "name": "Ближний",
            "longitude": 36.7,
            "latitude": 55.2,
            "orders": [{"product_id": "berry", "demand_kg": 40, "price_per_kg": 10}],
        },
        {
            "id": "next",
            "name": "Следующий",
            "longitude": 37.6,
            "latitude": 54.2,
            "orders": [{"product_id": "berry", "demand_kg": 40, "price_per_kg": 10}],
        },
    ]
    payload["vehicles"][0]["capacity_kg"] = 100
    payload["vehicles"][0]["max_stops"] = 2
    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert [stop["buyer_id"] for stop in body["trips"][0]["stops"]] == ["near"]
    assert body["trips"][0]["distance_km"] == 10
    assert body["trips"][0]["cost"] == 50
    assert body["profit"] == 350


def test_demo_fleet_has_three_vehicles_and_ten_buyers() -> None:
    response = client.get("/api/v1/demo/fleet")
    assert response.status_code == 200
    body = response.json()
    assert len(body["vehicles"]) == 3
    assert len(body["buyers"]) == 10
    assert "longitude" in body["farm"]


def test_three_vehicles_can_split_ten_buyers(monkeypatch) -> None:
    buyers = [
        {
            "id": f"buyer-{index}",
            "name": f"Покупатель {index}",
            "longitude": 36.6 + index * 0.05,
            "latitude": 55.1,
            "orders": [{"product_id": "berry", "demand_kg": 100, "price_per_kg": 10}],
        }
        for index in range(1, 11)
    ]
    payload = {
        "farm": {"name": "Хозяйство", "longitude": 36.6, "latitude": 55.1},
        "products": [
            {"id": "berry", "name": "Ягода", "stock_kg": 600, "max_delivery_hours": 24}
        ],
        "buyers": buyers,
        "vehicles": [
            {
                "id": f"vehicle-{letter}",
                "name": f"Машина {letter}",
                "capacity_kg": 200,
                "fuel_consumption_l_per_100km": 10,
                "fuel_price_rub_per_liter": 50,
                "max_trips": 1,
                "max_stops": 3,
                "available": True,
            }
            for letter in ("a", "b", "c")
        ],
    }
    ids = ["farm"] + [buyer["id"] for buyer in buyers]
    install_roads(monkeypatch, _mesh(ids, hours=0.5, km=10.0))

    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "optimal"
    used_vehicles = {trip["vehicle_id"] for trip in body["trips"]}
    served_buyers = {stop["buyer_id"] for trip in body["trips"] for stop in trip["stops"]}
    assert used_vehicles == {"vehicle-a", "vehicle-b", "vehicle-c"}
    assert len(body["trips"]) == 3
    assert len(served_buyers) == 6
    for trip in body["trips"]:
        assert len(trip["stops"]) == 2
        assert trip["load_kg"] == 200
        assert trip["waypoints"][0]["id"] == "farm"
        assert len(trip["waypoints"]) == 3
    assert body["revenue"] == 6000
    assert body["profit"] == round(body["revenue"] - body["transport_cost"], 2)
    leftover = {item["product_id"]: item for item in body["balances"]}["berry"]["leftover_kg"]
    assert leftover == 0


def test_plan_rejects_unknown_product() -> None:
    payload = _payload()
    payload["buyers"][0]["orders"][0]["product_id"] = "potato"
    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 422
