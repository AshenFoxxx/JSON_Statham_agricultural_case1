"""
Генератор интерактивной карты в стиле навигатора.
"""


def generate_map_html(route_data: dict, from_coords: tuple, to_coords: tuple, filepath: str) -> None:
    distance_km = route_data["distance_km"]
    duration_hours = route_data["duration_hours"]
    fuel_liters = route_data["fuel_liters"]
    fuel_cost = route_data["fuel_cost_rub"]

    start_lat, start_lng = from_coords[1], from_coords[0]
    end_lat, end_lng = to_coords[1], to_coords[0]

    geometry = route_data["geometry"]
    coords = geometry["coordinates"]

    import json
    coords_json = json.dumps(coords)

    # Используем шаблон с плейсхолдерами — никаких проблем с экранированием
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Маршрут грузовика</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0e1a; color: #fff; overflow: hidden; }
        #map { width: 100%; height: 100vh; background: #0a0e1a; }
        .route-summary { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); z-index: 1000; background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.98)); backdrop-filter: blur(20px); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 20px; padding: 20px 32px; min-width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,0.6); }
        .route-summary .header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
        .route-summary .header .truck-icon { font-size: 28px; }
        .route-summary .header h2 { font-size: 16px; font-weight: 600; color: #e2e8f0; letter-spacing: 0.5px; }
        .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
        .metric { text-align: center; }
        .metric .value { font-size: 28px; font-weight: 700; color: #38bdf8; line-height: 1; margin-bottom: 4px; }
        .metric .value.fuel { color: #a78bfa; }
        .metric .value.cost { color: #fbbf24; }
        .metric .label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
        .side-panel { position: absolute; top: 160px; right: 20px; z-index: 1000; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(20px); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 16px; padding: 20px; width: 280px; box-shadow: 0 15px 40px rgba(0,0,0,0.5); }
        .side-panel h3 { font-size: 14px; font-weight: 600; color: #94a3b8; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; }
        .detail-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(148, 163, 184, 0.1); }
        .detail-item:last-child { border-bottom: none; }
        .detail-item .detail-label { font-size: 13px; color: #94a3b8; display: flex; align-items: center; gap: 8px; }
        .detail-item .detail-value { font-size: 15px; font-weight: 600; color: #e2e8f0; }
        .custom-marker { display: flex; align-items: center; justify-content: center; }
        .marker-pin { width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.4); position: relative; }
        .marker-pin.start { background: #22c55e; }
        .marker-pin.end { background: #ef4444; }
        .marker-pin::after { content: ''; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 8px; height: 8px; background: white; border-radius: 50%; }
        .leaflet-popup-content-wrapper { background: rgba(15, 23, 42, 0.95); color: #e2e8f0; border-radius: 12px; border: 1px solid rgba(148, 163, 184, 0.2); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .leaflet-popup-tip { background: rgba(15, 23, 42, 0.95); }
        .leaflet-popup-content { margin: 12px 16px; font-size: 14px; line-height: 1.6; }
        .popup-title { font-weight: 600; font-size: 15px; margin-bottom: 4px; color: #f8fafc; }
        .popup-subtitle { color: #94a3b8; font-size: 12px; }
        .leaflet-control-zoom a { background: rgba(15, 23, 42, 0.9) !important; color: #e2e8f0 !important; border: 1px solid rgba(148, 163, 184, 0.2) !important; }
        .leaflet-control-zoom a:hover { background: rgba(30, 41, 59, 0.95) !important; }
        .leaflet-control-attribution { background: rgba(15, 23, 42, 0.8) !important; color: #64748b !important; font-size: 10px !important; }
        .leaflet-control-attribution a { color: #38bdf8 !important; }
    </style>
</head>
<body>
    <div id="map"></div>

    <div class="route-summary">
        <div class="header">
            <span class="truck-icon">&#128666;</span>
            <h2>МАРШРУТ ГРУЗОВИКА</h2>
        </div>
        <div class="metrics">
            <div class="metric">
                <div class="value">DISTANCE_VAL км</div>
                <div class="label">расстояние</div>
            </div>
            <div class="metric">
                <div class="value">TIME_VAL ч</div>
                <div class="label">время в пути</div>
            </div>
            <div class="metric">
                <div class="value fuel">FUEL_VAL л</div>
                <div class="label">расход топлива</div>
            </div>
        </div>
    </div>

    <div class="side-panel">
        <h3>Детали маршрута</h3>
        <div class="detail-item">
            <span class="detail-label">&#128666; Расход</span>
            <span class="detail-value">FUEL_VAL л</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">&#128176; Стоимость</span>
            <span class="detail-value" style="color: #fbbf24;">COST_VAL руб</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">&#128339; Время</span>
            <span class="detail-value">TIME_VAL ч</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">&#128205; Расстояние</span>
            <span class="detail-value">DISTANCE_VAL км</span>
        </div>
    </div>

    <div id="js-data" style="display:none;">
        {"coords": COORDS_PLACEHOLDER, "startLat": START_LAT_PLACEHOLDER, "startLng": START_LNG_PLACEHOLDER, "endLat": END_LAT_PLACEHOLDER, "endLng": END_LNG_PLACEHOLDER}
    </div>

    <script src="ROUTE_MAP.js"></script>
</body>
</html>"""

    # Заменяем плейсхолдеры
    html = html.replace("DISTANCE_VAL", f"{distance_km:.0f}")
    html = html.replace("TIME_VAL", f"{duration_hours:.1f}")
    html = html.replace("FUEL_VAL", f"{fuel_liters:.0f}")
    html = html.replace("COST_VAL", f"{fuel_cost:,.0f}")
    html = html.replace("START_LAT_PLACEHOLDER", str(start_lat))
    html = html.replace("START_LNG_PLACEHOLDER", str(start_lng))
    html = html.replace("END_LAT_PLACEHOLDER", str(end_lat))
    html = html.replace("END_LNG_PLACEHOLDER", str(end_lng))
    html = html.replace("COORDS_PLACEHOLDER", coords_json)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    # Отдельный JS-файл — никаких проблем с экранированием
    js = """// Загружаем данные из скрытого блока
const data = JSON.parse(document.getElementById('js-data').textContent);
const routeCoords = data.coords;
const routePath = routeCoords.map(c => [c[1], c[0]]);

// Инициализация карты
const map = L.map('map').setView([data.startLat, data.startLng], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 18
}).addTo(map);

// Кастомные маркеры
const createMarker = (lat, lng, className, title, subtitle) => {
    const icon = L.divIcon({
        className: 'custom-marker',
        html: '<div class="marker-pin ' + className + '"></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });
    return L.marker([lat, lng], { icon: icon })
        .addTo(map)
        .bindPopup('<div class="popup-title">' + title + '</div><div class="popup-subtitle">' + subtitle + '</div>');
};

createMarker(data.startLat, data.startLng, 'start', 'Старт', 'Точка отправления');
createMarker(data.endLat, data.endLng, 'end', 'Финиш', 'Точка прибытия');

// Маршрут
L.polyline(routePath, {
    color: '#38bdf8',
    weight: 6,
    opacity: 0.9,
    lineJoin: 'round',
    lineCap: 'round'
}).addTo(map);

// Автоподгонка
const bounds = L.latLngBounds(routePath);
map.fitBounds(bounds, { padding: [80, 80] });
"""

    # Сохраняем JS рядом с HTML
    js_path = filepath.replace('.html', '.js')
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
