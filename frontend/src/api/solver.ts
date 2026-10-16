import type {
  SolverPlanRequest,
  SolverFarm,
  SolverProduct,
  SolverBuyer,
  SolverVehicle,
  SolverPlanResponse,
} from './client'
import { solverApi } from './client'

export async function callSolver(
  farm: SolverFarm,
  products: SolverProduct[],
  buyers: SolverBuyer[],
  vehicles: SolverVehicle[]
): Promise<SolverPlanResponse> {
  const body: SolverPlanRequest = { farm, products, buyers, vehicles }
  return solverApi.plan(body)
}
