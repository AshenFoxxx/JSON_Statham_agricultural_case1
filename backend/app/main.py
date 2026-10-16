from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.demo_data import demo_request
from app.planning import build_plan
from app.routing import RouteError, fetch_route
from app.schemas import PlanRequest, PlanResponse, RouteRequest, RouteResponse

app = FastAPI(
    title="Спаси урожай",
    version="0.1.0",
    description="Считает план поставок и маршрут по дорогам. Карта живёт в папке frontend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/demo", response_model=PlanRequest)
def demo() -> PlanRequest:
    return demo_request()


@app.post("/api/v1/plan", response_model=PlanResponse)
def plan(body: PlanRequest) -> PlanResponse:
    try:
        return build_plan(body)
    except RouteError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/v1/route", response_model=RouteResponse)
def route(body: RouteRequest) -> RouteResponse:
    points = [(point.id, point.longitude, point.latitude) for point in body.points]
    try:
        return fetch_route(
            points,
            body.fuel_consumption_l_per_100km,
            body.fuel_price_rub_per_liter,
        )
    except RouteError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
