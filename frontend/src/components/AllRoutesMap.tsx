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

export const TRIP_COLORS = ['#0284c7', '#f59e0b', '#7c3aed', '#059669', '#db2777']

export function tripColor(index: number) {
  return TRIP_COLORS[index % TRIP_COLORS.length]
}

export type OverviewRoute = {
  coordinates: number[][]
  color: string
}

export type MapBuyer = {
  name: string
  longitude: number
  latitude: number
  color?: string
}

type AllRoutesMapProps = {
  routes: OverviewRoute[]
  farm?: { longitude: number; latitude: number } | null
  buyers?: MapBuyer[]
  className?: string
}

function buyerStyle(name: string, color: string) {
  return new Style({
    image: new Circle({
      radius: 7,
      fill: new Fill({ color }),
      stroke: new Stroke({ color: '#ffffff', width: 2 }),
    }),
    text: new Text({
      text: name,
      offsetY: -14,
      font: '12px sans-serif',
      fill: new Fill({ color: '#111827' }),
      stroke: new Stroke({ color: '#ffffff', width: 3 }),
    }),
  })
}

export default function AllRoutesMap({ routes, farm, buyers = [], className }: AllRoutesMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const routesKey = JSON.stringify(routes)
  const buyersKey = JSON.stringify(buyers)

  useEffect(() => {
    const node = containerRef.current
    if (!node) {
      return
    }
    const features: Feature[] = []
    for (const route of routes) {
      if (route.coordinates.length < 2) {
        continue
      }
      const lineCoords = route.coordinates.map(([lon, lat]) => fromLonLat([lon, lat]))
      const line = new Feature({ geometry: new LineString(lineCoords) })
      line.setStyle(
        new Style({
          stroke: new Stroke({ color: route.color, width: 5 }),
        })
      )
      features.push(line)
    }
    for (const buyer of buyers) {
      const point = new Feature({
        geometry: new Point(fromLonLat([buyer.longitude, buyer.latitude])),
      })
      point.setStyle(buyerStyle(buyer.name, buyer.color || '#64748b'))
      features.push(point)
    }
    if (farm) {
      const farmPoint = new Feature({
        geometry: new Point(fromLonLat([farm.longitude, farm.latitude])),
      })
      farmPoint.setStyle(
        new Style({
          image: new Circle({
            radius: 8,
            fill: new Fill({ color: '#16a34a' }),
            stroke: new Stroke({ color: '#ffffff', width: 2 }),
          }),
          text: new Text({
            text: 'Хозяйство',
            offsetY: -16,
            font: '12px sans-serif',
            fill: new Fill({ color: '#166534' }),
            stroke: new Stroke({ color: '#ffffff', width: 3 }),
          }),
        })
      )
      features.push(farmPoint)
    }
    if (features.length === 0) {
      return
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
        center: farm
          ? fromLonLat([farm.longitude, farm.latitude])
          : fromLonLat([36.61, 55.1]),
        zoom: 8,
      }),
    })
    map.getView().fit(vector.getExtent(), { padding: [36, 36, 36, 36], maxZoom: 13 })
    return () => {
      map.setTarget(undefined)
    }
  }, [routesKey, buyersKey, farm?.longitude, farm?.latitude])

  if (routes.length === 0 && !farm && buyers.length === 0) {
    return null
  }

  return (
    <div
      ref={containerRef}
      className={className || 'h-96 w-full rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden'}
    />
  )
}
