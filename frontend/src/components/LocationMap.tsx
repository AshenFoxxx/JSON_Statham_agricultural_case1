import RouteLineMap from './RouteLineMap'

type LocationMapProps = {
  longitude: number
  latitude: number
  title?: string
}

export default function LocationMap({ longitude, latitude, title }: LocationMapProps) {
  return (
    <div className="mt-6">
      <RouteLineMap coordinates={[[longitude, latitude]]} title={title} />
    </div>
  )
}
