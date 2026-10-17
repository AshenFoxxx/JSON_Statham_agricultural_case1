from ortools.sat.python import cp_model

from app.routing import clear_matrix_cache, fetch_matrix, process_route, process_table
from app.solver_cp_sat import _status_from_cpsat
from app.schemas import SolverStatus


def test_osrm_response_becomes_plan_legs() -> None:
    route = {
        "distance": 150000,
        "duration": 7200,
        "legs": [
            {"distance": 100000, "duration": 3600},
            {"distance": 50000, "duration": 3600},
        ],
        "geometry": {"type": "LineString", "coordinates": [[37.6, 55.7], [36.2, 54.5]]},
    }
    points = [("farm", 37.6, 55.7), ("kaluga", 36.2, 54.5), ("tula", 37.6, 54.2)]
    result = process_route(route, points, 35, 62)

    assert result["duration_hours"] == 2
    assert result["legs"] == [
        {"from_id": "farm", "to_id": "kaluga", "distance_km": 100, "hours": 1},
        {"from_id": "kaluga", "to_id": "tula", "distance_km": 50, "hours": 1},
    ]
    assert result["waypoints"][0] == {"id": "farm", "longitude": 37.6, "latitude": 55.7}
    assert result["waypoints"][2]["latitude"] == 54.2


def test_osrm_table_becomes_hours_and_kilometers() -> None:
    points = [("farm", 36.6, 55.1), ("kaluga", 36.2, 54.5)]
    graph = process_table(
        {
            "durations": [[0, 3600], [7200, 0]],
            "distances": [[0, 10000], [None, 0]],
        },
        points,
    )
    assert graph[("farm", "kaluga")] == (1.0, 10.0)
    assert ("kaluga", "farm") not in graph


def test_matrix_cache_skips_osrm_when_coordinates_unchanged(monkeypatch) -> None:
    clear_matrix_cache()
    calls: list[str] = []

    class _Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "code": "Ok",
                "durations": [[0, 3600], [3600, 0]],
                "distances": [[0, 10000], [10000, 0]],
            }

    def fake_get(url: str, timeout: int = 30):
        calls.append(url)
        return _Response()

    monkeypatch.setattr("requests.get", fake_get)
    points = [("farm", 36.6103, 55.0969), ("near", 36.7, 55.2)]
    first = fetch_matrix(points)
    second = fetch_matrix(list(reversed(points)))
    assert first[("farm", "near")] == (1.0, 10.0)
    assert second[("farm", "near")] == first[("farm", "near")]
    assert len(calls) == 1

    fetch_matrix([("farm", 36.6103, 55.0969), ("near", 36.8, 55.2)])
    assert len(calls) == 2


def test_cpsat_feasible_is_not_called_optimal() -> None:
    status, message = _status_from_cpsat(cp_model.FEASIBLE)
    assert status == SolverStatus.FEASIBLE
    assert "оптимум" in message.lower()
    status, _message = _status_from_cpsat(cp_model.OPTIMAL)
    assert status == SolverStatus.OPTIMAL
    status, _message = _status_from_cpsat(cp_model.UNKNOWN)
    assert status == SolverStatus.NOT_SOLVED
