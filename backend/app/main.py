from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.demo_data import demo_request
from app.planning import build_plan
from app.schemas import PlanRequest, PlanResponse

app = FastAPI(
    title="Спаси урожай",
    version="0.1.0",
    description="Принимает культуры, заказы и машины и возвращает план поставок с выручкой, затратами и прибылью.",
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
    return build_plan(body)
