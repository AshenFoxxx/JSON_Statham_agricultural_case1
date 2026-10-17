import { useEffect, useRef } from 'react'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import XYZ from 'ol/source/XYZ'
import Feature from 'ol/Feature'
import LineString from 'ol/geom/LineString'
import Point from 'ol/geom/Point'
import { fromLonLat } from 'ol/proj'
import { Style, Stroke, Circle, Fill, Text } from 'ol/style'
import 'ol/ol.css'

type RouteBuyer = {
  name: string
  longitude: number
  latitude: number
}

type RouteLineMapProps = {
  coordinates: number[][]
  title?: string
  color?: string
  buyers?: RouteBuyer[]
}

export default function RouteLineMap({ coordinates, title, color = '#0284c7', buyers = [] }: RouteLineMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const buyersKey = JSON.stringify(buyers)

  useEffect(() => {
    const node = containerRef.current
    if (!node || coordinates.length < 1) {
      return
    }
    const lineCoords = coordinates.map(([lon, lat]) => fromLonLat([lon, lat]))
    const features: Feature[] = []
    if (lineCoords.length >= 2) {
      const line = new Feature({ geometry: new LineString(lineCoords) })
      line.setStyle(
        new Style({
          stroke: new Stroke({ color, width: 5 }),
        })
      )
      features.push(line)
    }
    const start = new Feature({ geometry: new Point(lineCoords[0]) })
    start.setStyle(
      new Style({
        image: new Circle({
          radius: 7,
          fill: new Fill({ color: '#22c55e' }),
          stroke: new Stroke({ color: '#ffffff', width: 2 }),
        }),
      })
    )
    features.push(start)
    if (lineCoords.length >= 2) {
      const end = new Feature({ geometry: new Point(lineCoords[lineCoords.length - 1]) })
      end.setStyle(
        new Style({
          image: new Circle({
            radius: 6,
            fill: new Fill({ color: '#86efac' }),
            stroke: new Stroke({ color: '#ffffff', width: 2 }),
          }),
        })
      )
      features.push(end)
    }
    for (const buyer of buyers) {
      const point = new Feature({
        geometry: new Point(fromLonLat([buyer.longitude, buyer.latitude])),
      })
      point.setStyle(
        new Style({
          image: new Circle({
            radius: 7,
            fill: new Fill({ color: '#f59e0b' }),
            stroke: new Stroke({ color: '#ffffff', width: 2 }),
          }),
          text: new Text({
            text: buyer.name,
            offsetY: -14,
            font: '12px sans-serif',
            fill: new Fill({ color: '#111827' }),
            stroke: new Stroke({ color: '#ffffff', width: 3 }),
          }),
        })
      )
      features.push(point)
    }
    const vector = new VectorSource({ features })
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
        new VectorLayer({ source: vector }),
      ],
      view: new View({
        center: lineCoords[0],
        zoom: lineCoords.length >= 2 ? 8 : 13,
      }),
    })
    if (lineCoords.length >= 2) {
      map.getView().fit(vector.getExtent(), { padding: [28, 28, 28, 28], maxZoom: 14 })
    }
    return () => {
      map.setTarget(undefined)
    }
  }, [coordinates, color, buyersKey, buyers])

  if (coordinates.length < 1) {
    return null
  }

  return (
    <div
      ref={containerRef}
      title={title}
      className="h-64 w-full rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden"
    />
  )
}
