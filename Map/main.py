"""
Точка входа для планировщика маршрутов.

Использование:
    python main.py --from "55.7558,37.6173" --to "59.9343,30.3351"
    python main.py --from "55.7558,37.6173" --to "59.9343,30.3351" --fuel-price 65 --fuel-consumption 40

Аргументы:
    --from              Начальная точка (longitude,latitude)
    --to                Конечная точка (longitude,latitude)
    --fuel-price        Цена топлива (руб/л), по умолчанию: 62.0
    --fuel-consumption  Расход топлива (л/100км), по умолчанию: 35.0
    --output            Папка для выходных файлов (по умолчанию: output)
"""

import argparse
import os
import sys

from route_planner import get_route, save_route_json, save_geometry
from map_generator import generate_map_html
from config import OUTPUT_DIR, OUTPUT_JSON_FILE, OUTPUT_HTML_FILE, FRONTEND_DIR


def parse_args():
    parser = argparse.ArgumentParser(description="Планировщик маршрутов для грузовиков")
    parser.add_argument(
        "--from",
        dest="from_coords",
        required=True,
        help="Начальная точка: longitude,latitude (например: 55.7558,37.6173)",
    )
    parser.add_argument(
        "--to",
        dest="to_coords",
        required=True,
        help="Конечная точка: longitude,latitude (например: 59.9343,30.3351)",
    )
    parser.add_argument(
        "--fuel-price",
        type=float,
        default=62.0,
        help="Цена топлива (руб/л), по умолчанию: 62.0",
    )
    parser.add_argument(
        "--fuel-consumption",
        type=float,
        default=35.0,
        help="Расход топлива (л/100км), по умолчанию: 35.0",
    )
    parser.add_argument(
        "--output",
        default=OUTPUT_DIR,
        help="Папка для выходных файлов",
    )
    return parser.parse_args()


def parse_coords(coords_str: str) -> tuple:
    """
    Парсит строку координат в кортеж (longitude, latitude).
    """
    parts = coords_str.split(",")
    if len(parts) != 2:
        raise ValueError(f"Неверный формат координат: {coords_str}. Ожидается: longitude,latitude")
    return (float(parts[0]), float(parts[1]))


def main():
    args = parse_args()

    try:
        from_coords = parse_coords(args.from_coords)
        to_coords = parse_coords(args.to_coords)
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, OUTPUT_JSON_FILE)
    geometry_path = os.path.join(output_dir, "route_geometry.json")
    html_path = os.path.join(output_dir, OUTPUT_HTML_FILE)

    print(f"Маршрут: {from_coords} -> {to_coords}")
    print(f"Цена топлива: {args.fuel_price} руб/л")
    print(f"Расход топлива: {args.fuel_consumption} л/100км")
    print("Запрашиваю маршрут...")

    try:
        route_data = get_route(
            from_coords, to_coords,
            fuel_consumption=args.fuel_consumption,
            fuel_price=args.fuel_price
        )
    except Exception as e:
        print(f"Ошибка при получении маршрута: {e}")
        sys.exit(1)

    print(f"\nРезультат:")
    print(f"  Расстояние: {route_data['distance_km']} км")
    print(f"  Время в пути: {route_data['duration_hours']:.1f} ч")
    print(f"  Расход топлива: {route_data['fuel_liters']} л")
    print(f"  Стоимость топлива: {route_data['fuel_cost_rub']:.0f} руб")

    save_route_json(route_data, json_path)
    print(f"\nJSON сохранён: {json_path}")

    save_geometry(route_data["geometry"], geometry_path)
    print(f"Геометрия сохранена: {geometry_path}")

    generate_map_html(route_data, from_coords, to_coords, html_path)
    print(f"Карта сохранена: {html_path}")

    print("\nГотово!")


if __name__ == "__main__":
    main()
