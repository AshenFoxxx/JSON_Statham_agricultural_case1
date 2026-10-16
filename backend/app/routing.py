"""Расчёт маршрута через OSRM. Координаты: longitude, latitude."""

OSRM_API_URL = "http://router.project-osrm.org/route/v1/driving"
OSRM_TABLE_URL = "http://router.project-osrm.org/table/v1/driving"


class RouteError(Exception):
    """OSRM не ответил или не нашёл маршрут."""


def fuel_cost_rub(distance_km: float, consumption_l_per_100km: float, price_rub_per_liter: float) -> float:
    """Стоимость топлива: (км / 100) × расход × цена литра."""
    return (distance_km / 100.0) * consumption_l_per_100km * price_rub_per_liter


def fetch_matrix(points: list[tuple[str, float, float]]) -> dict[tuple[str, str], tuple[float, float]]:
    """Часы и километры между всеми точками. Ключ — (from_id, to_id)."""
    if len(points) < 2:
        raise RouteError("Нужны минимум две точки")

    import requests

    coords = ";".join(f"{lon},{lat}" for _point_id, lon, lat in points)
    url = f"{OSRM_TABLE_URL}/{coords}?annotations=duration,distance"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RouteError("Не удалось получить расстояния от OSRM") from exc

    if data.get("code") != "Ok":
        raise RouteError("OSRM не посчитал расстояния")
    return process_table(data, points)


def process_table(
    data: dict,
    points: list[tuple[str, float, float]],
) -> dict[tuple[str, str], tuple[float, float]]:
    """Матрица OSRM: секунды и метры становятся часами и километрами."""
    durations = data.get("durations")
    distances = data.get("distances")
    if not durations or not distances or len(durations) != len(points) or len(distances) != len(points):
        raise RouteError("OSRM вернул неполную матрицу расстояний")

    graph: dict[tuple[str, str], tuple[float, float]] = {}
    for origin_index, origin in enumerate(points):
        duration_row = durations[origin_index]
        distance_row = distances[origin_index]
        if len(duration_row) != len(points) or len(distance_row) != len(points):
            raise RouteError("OSRM вернул неполную матрицу расстояний")
        for dest_index, dest in enumerate(points):
            if origin_index == dest_index:
                continue
            seconds = duration_row[dest_index]
            meters = distance_row[dest_index]
            if seconds is None or meters is None:
                continue
            graph[(origin[0], dest[0])] = (seconds / 3600.0, meters / 1000.0)
    return graph


def fetch_route(
    points: list[tuple[str, float, float]],
    fuel_consumption: float = 35.0,
    fuel_price: float = 62.0,
) -> dict:
    """Строит маршрут через точки в заданном порядке. Минимум две точки."""
    if len(points) < 2:
        raise RouteError("Нужны минимум две точки")

    import requests

    coords = ";".join(f"{lon},{lat}" for _point_id, lon, lat in points)
    url = f"{OSRM_API_URL}/{coords}?overview=full&geometries=geojson"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RouteError("Не удалось получить маршрут от OSRM") from exc

    if data.get("code") != "Ok" or not data.get("routes"):
        raise RouteError("OSRM не нашёл маршрут")
    return process_route(data["routes"][0], points, fuel_consumption, fuel_price)


def process_route(
    route: dict,
    points: list[tuple[str, float, float]],
    fuel_consumption: float,
    fuel_price: float,
) -> dict:
    """Превращает ответ OSRM в сводку. Поле legs подходит для POST /api/v1/plan."""
    osrm_legs = route.get("legs") or []
    if len(osrm_legs) != len(points) - 1:
        raise RouteError("OSRM вернул не все перегоны между точками")

    distance_km = route["distance"] / 1000.0
    duration_hours = route["duration"] / 3600.0
    fuel_liters = (distance_km / 100.0) * fuel_consumption

    legs = []
    for index, leg in enumerate(osrm_legs):
        legs.append(
            {
                "from_id": points[index][0],
                "to_id": points[index + 1][0],
                "distance_km": round(leg["distance"] / 1000.0, 2),
                "hours": round(leg["duration"] / 3600.0, 2),
            }
        )

    return {
        "distance_km": round(distance_km, 2),
        "duration_hours": round(duration_hours, 2),
        "fuel_liters": round(fuel_liters, 2),
        "fuel_cost_rub": round(fuel_cost_rub(distance_km, fuel_consumption, fuel_price), 2),
        "legs": legs,
        "waypoints": [
            {"id": point_id, "longitude": lon, "latitude": lat}
            for point_id, lon, lat in points
        ],
        "geometry": route["geometry"],
    }
