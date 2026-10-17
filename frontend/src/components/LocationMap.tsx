type LocationMapProps = {
  longitude: number
  latitude: number
  title?: string
}

function osmEmbed(longitude: number, latitude: number, span = 0.12) {
  const minLon = longitude - span
  const minLat = latitude - span
  const maxLon = longitude + span
  const maxLat = latitude + span
  return (
    'https://www.openstreetmap.org/export/embed.html?bbox=' +
    `${minLon}%2C${minLat}%2C${maxLon}%2C${maxLat}` +
    `&layer=mapnik&marker=${latitude}%2C${longitude}`
  )
}

export default function LocationMap({ longitude, latitude, title }: LocationMapProps) {
  return (
    <iframe
      title={title || 'Карта'}
      className="mt-6 h-64 w-full rounded-lg border border-gray-200 dark:border-gray-600"
      src={osmEmbed(longitude, latitude)}
    />
  )
}
