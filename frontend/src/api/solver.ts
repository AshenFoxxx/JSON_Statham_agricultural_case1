import { solverApi } from './client'

export async function callSolver(
  products: any[],
  buyers: any[],
  vehicles: any[]
): Promise<any> {
  return solverApi.plan({ products, buyers, vehicles })
}
