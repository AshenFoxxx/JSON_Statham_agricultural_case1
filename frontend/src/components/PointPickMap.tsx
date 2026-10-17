import { useEffect, useRef } from 'react'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import XYZ from 'ol/source/XYZ'
import Feature from 'ol/Feature'
import Point from 'ol/geom/Point'
import { fromLonLat, toLonLat } from 'ol/proj'
import { Style, Circle, Fill, Stroke } from 'ol/style'
import 'ol/ol.css'

const OBNINSK: [number, number] = [36.6103, 55.0969]

type PointPickMapProps = {
  longitude?: number
  latitude?: number
  defaultLongitude?: number
  defaultLatitude?: number
  onPick: (longitude: number, latitude: number) => void
}

function hasCoords(longitude?: number, latitude?: number) {
  return Number.isFinite(longitude) && Number.isFinite(latitude)
}

function roundCoord(value: number) {
  return Math.round(value * 1e6) / 1e6
}

export default function PointPickMap({
  longitude,
  latitude,
  defaultLongitude,
  defaultLatitude,
  onPick,
}: PointPickMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const sourceRef = useRef<VectorSource | null>(null)
  const onPickRef = useRef(onPick)
  onPickRef.current = onPick

  useEffect(() => {
    const node = containerRef.current
    if (!node) {
      return
    }

    const source = new VectorSource()
    sourceRef.current = source
    const centerLon = hasCoords(longitude, latitude) ? longitude! : (defaultLongitude ?? OBNINSK[0])
    const centerLat = hasCoords(longitude, latitude) ? latitude! : (defaultLatitude ?? OBNINSK[1])

    const map = new Map({
      target: node,
      layers: [
        new TileLayer({
          source: new XYZ({
            url: 'https://tile.openstreetmap.de/{z}/{x}/{y}.png',
            attributions: '© OpenStreetMap contributors',
            maxZoom: 19,
          }),
        }),
        new VectorLayer({ source }),
      ],
      view: new View({
        center: fromLonLat([centerLon, centerLat]),
        zoom: 12,
      }),
    })

    map.on('singleclick', (event) => {
      const [lon, lat] = toLonLat(event.coordinate)
      onPickRef.current(roundCoord(lon), roundCoord(lat))
    })

    const timeout = window.setTimeout(() => map.updateSize(), 50)

    return () => {
      window.clearTimeout(timeout)
      map.setTarget(undefined)
      sourceRef.current = null
    }
    // Map is created when the modal mounts; coords are applied in the marker effect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const source = sourceRef.current
    if (!source) {
      return
    }
    source.clear()
    if (!hasCoords(longitude, latitude)) {
      return
    }
    const marker = new Feature({ geometry: new Point(fromLonLat([longitude!, latitude!])) })
    marker.setStyle(
      new Style({
        image: new Circle({
          radius: 8,
          fill: new Fill({ color: '#0284c7' }),
          stroke: new Stroke({ color: '#ffffff', width: 2 }),
        }),
      })
    )
    source.addFeature(marker)
  }, [longitude, latitude])

  return (
    <div>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
        Кликните по карте, чтобы поставить точку
      </p>
      <div
        ref={containerRef}
        className="h-56 w-full rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden cursor-crosshair"
      />
    </div>
  )
}
