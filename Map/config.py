"""
Конфигурация для планировщика маршрутов.
"""

# OSRM Public API (бесплатный, open-source)
OSRM_API_URL = "http://router.project-osrm.org/route/v1/driving"

# Значения по умолчанию (можно переопредить через CLI)
DEFAULT_FUEL_CONSUMPTION_L_PER_100KM = 35.0
DEFAULT_FUEL_PRICE_PER_LITER = 62.0

# Формат вывода
OUTPUT_DIR = "output"
OUTPUT_JSON_FILE = "route.json"
OUTPUT_HTML_FILE = "route_map.html"
GEOMETRY_FILE = "route_geometry.json"
FRONTEND_DIR = "frontend"
