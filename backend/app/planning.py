from app.schemas import PlanRequest, PlanResponse
from app.solver import solve_plan


def build_plan(request: PlanRequest) -> PlanResponse:
    return solve_plan(request)
