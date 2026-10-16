"""
Планировщик маршрутов.
Использует OSRM API для получения оптимального маршрута между двумя точками.
"""

import json
import requests
from config import OSRM_API_URL


def get_route(from_coords: tuple, to_coords: tuple, fuel_consumption: float = 35.0,
              fuel_price: float = 62.0) -> dict:
    """
    Запрашивает маршрут через OSRM API и рассчитывает расход топлива.

    Args:
        from_coords: (longitude, latitude) начальной точки
        to_coords: (longitude, latitude) конечной точки
        fuel_consumption: расход топлива (л/100км)
        fuel_price: цена топлива (руб/л)

    Returns:
        Словарь с данными маршрута
    """
    coords = f"{from_coords[0]},{from_coords[1]};{to_coords[0]},{to_coords[1]}"
    url = f"{OSRM_API_URL}/{coords}?overview=simplified&geometries=geojson"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise RuntimeError("OSRM API не нашёл маршрут")

    route = data["routes"][0]
    return _process_route(route, fuel_consumption, fuel_price)


def _process_route(route: dict, fuel_consumption: float, fuel_price: float) -> dict:
    """
    Обрабатывает ответ OSRM и добавляет расчёты топлива.
    """
    distance_meters = route["distance"]
    distance_km = distance_meters / 1000.0

    duration_seconds = route["duration"]
    duration_hours = duration_seconds / 3600.0

    fuel_needed = (distance_km / 100.0) * fuel_consumption
    fuel_cost = fuel_needed * fuel_price

    return {
        "distance_km": round(distance_km, 2),
        "duration_hours": round(duration_hours, 2),
        "fuel_liters": round(fuel_needed, 2),
        "fuel_cost_rub": round(fuel_cost, 2),
        "geometry": route["geometry"],
    }


def calculate_fuel(distance_km: float, fuel_consumption: float = 35.0,
                   fuel_price: float = 62.0) -> dict:
    """
    Рассчитывает расход топлива для заданного расстояния.

    Args:
        distance_km: расстояние в километрах
        fuel_consumption: расход топлива (л/100км)
        fuel_price: цена топлива (руб/л)

    Returns:
        Словарь с расчётами топлива
    """
    fuel_liters = (distance_km / 100.0) * fuel_consumption
    fuel_cost = fuel_liters * fuel_price

    return {
        "distance_km": round(distance_km, 2),
        "fuel_liters": round(fuel_liters, 2),
        "fuel_cost_rub": round(fuel_cost, 2),
    }


def save_route_json(route_data: dict, filepath: str) -> None:
    """
    Сохраняет данные маршрута в JSON файл (только ключевые данные).
    Геометрия сохраняется отдельно.

    Args:
        route_data: данные маршрута
        filepath: путь к файлу
    """
    summary = {
        "distance_km": route_data["distance_km"],
        "duration_hours": route_data["duration_hours"],
        "fuel_liters": route_data["fuel_liters"],
        "fuel_cost_rub": route_data["fuel_cost_rub"],
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def save_geometry(geometry: dict, filepath: str) -> None:
    """
    Сохраняет геометрию маршрута в отдельный JSON файл.

    Args:
        geometry: GeoJSON геометрия маршрута
        filepath: путь к файлу
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(geometry, f, ensure_ascii=False, indent=2)
