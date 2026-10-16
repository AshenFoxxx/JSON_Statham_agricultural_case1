export async function callSolver(
  products: any[],
  buyers: any[],
  vehicles: any[]
): Promise<any> {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  
  const response = await fetch(`${apiUrl}/api/v1/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ products, buyers, vehicles }),
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}
