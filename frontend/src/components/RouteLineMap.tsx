type RouteLineMapProps = {
  coordinates: number[][]
  title?: string
}

function bbox(coordinates: number[][]) {
  const lons = coordinates.map((point) => point[0])
  const lats = coordinates.map((point) => point[1])
  const minLon = Math.min(...lons)
  const maxLon = Math.max(...lons)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  const padLon = Math.max((maxLon - minLon) * 0.2, 0.04)
  const padLat = Math.max((maxLat - minLat) * 0.2, 0.04)
  return [minLon - padLon, minLat - padLat, maxLon + padLon, maxLat + padLat]
}

export default function RouteLineMap({ coordinates, title }: RouteLineMapProps) {
  if (coordinates.length === 0) {
    return null
  }
  const [minLon, minLat, maxLon, maxLat] = bbox(coordinates)
  const start = coordinates[0]
  const src =
    'https://www.openstreetmap.org/export/embed.html?bbox=' +
    `${minLon}%2C${minLat}%2C${maxLon}%2C${maxLat}` +
    `&layer=mapnik&marker=${start[1]}%2C${start[0]}`
  return (
    <iframe
      title={title || 'Маршрут'}
      className="h-64 w-full rounded-lg border border-gray-200 dark:border-gray-600"
      src={src}
    />
  )
}
