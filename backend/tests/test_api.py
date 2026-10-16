from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _payload() -> dict:
    return {
        "products": [
            {"id": "berry", "name": "Ягода", "stock_kg": 100, "max_delivery_hours": 5},
            {"id": "apple", "name": "Яблоко", "stock_kg": 100, "max_delivery_hours": 20},
        ],
        "buyers": [
            {
                "id": "near",
                "name": "Ближний",
                "travel_time_hours": 2,
                "orders": [
                    {"product_id": "berry", "demand_kg": 100, "price_per_kg": 10},
                    {"product_id": "apple", "demand_kg": 50, "price_per_kg": 1},
                ],
            },
            {
                "id": "far",
                "name": "Дальний",
                "travel_time_hours": 10,
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
                "cost_per_trip": 50,
                "max_trips": 1,
                "available": True,
            }
        ],
    }


def test_plan_uses_request_prices() -> None:
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
    assert costly.json()["profit"] == 1950


def test_plan_respects_stock_demand_capacity_and_time() -> None:
    response = client.post("/api/v1/plan", json=client.get("/api/v1/demo").json())
    assert response.status_code == 200
    body = response.json()
    request = client.get("/api/v1/demo").json()
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
    assert body["profit"] == round(body["revenue"] - body["transport_cost"], 2)


def test_unavailable_vehicle_is_not_used() -> None:
    payload = _payload()
    payload["vehicles"][0]["available"] = False
    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["shipments"] == []
    assert body["profit"] == 0
    balances = {item["product_id"]: item for item in body["balances"]}
    assert balances["berry"]["leftover_kg"] == 100


def test_one_trip_serves_two_buyers() -> None:
    payload = _payload()
    payload["products"] = [
        {"id": "berry", "name": "Ягода", "stock_kg": 80, "max_delivery_hours": 5}
    ]
    payload["buyers"] = [
        {
            "id": "near",
            "name": "Ближний",
            "travel_time_hours": 1,
            "orders": [{"product_id": "berry", "demand_kg": 40, "price_per_kg": 10}],
        },
        {
            "id": "next",
            "name": "Следующий",
            "travel_time_hours": 4,
            "orders": [{"product_id": "berry", "demand_kg": 40, "price_per_kg": 10}],
        },
    ]
    payload["vehicles"][0]["capacity_kg"] = 100
    payload["vehicles"][0]["max_stops"] = 2
    payload["legs"] = [
        {"from_id": "farm", "to_id": "near", "hours": 1},
        {"from_id": "near", "to_id": "next", "hours": 1},
        {"from_id": "farm", "to_id": "next", "hours": 4},
    ]
    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["profit"] == 750
    assert len(body["trips"]) == 1
    assert [stop["buyer_id"] for stop in body["trips"][0]["stops"]] == ["near", "next"]
    assert body["trips"][0]["cost"] == 50
    assert sorted(item["buyer_id"] for item in body["shipments"]) == ["near", "next"]


def test_plan_rejects_unknown_product() -> None:
    payload = _payload()
    payload["buyers"][0]["orders"][0]["product_id"] = "potato"
    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 422
