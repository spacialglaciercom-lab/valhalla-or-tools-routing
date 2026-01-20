'use client';

import { useEffect, useRef, memo } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useAppStore } from '@/lib/store';
import { decodePolyline } from '@/lib/map-utils';
import type { RouteTrip, IsochroneFeature } from '@/types/valhalla';

interface MapProps {
  className?: string;
}

const MapComponent = memo(function Map({ className }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const routeLayerRef = useRef<string | null>(null);
  const isochroneLayersRef = useRef<string[]>([]);

  const { route, isochrone, ui, addWaypoint } = useAppStore();

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'raster-tiles': {
            type: 'raster',
            tiles: [
              'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            ],
            tileSize: 256,
            attribution:
              '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          },
        },
        layers: [
          {
            id: 'simple-tiles',
            type: 'raster',
            source: 'raster-tiles',
            minzoom: 0,
            maxzoom: 22,
          },
        ],
      },
      center: [-122.4194, 37.7749], // Default to San Francisco
      zoom: 12,
    });

    // Add click handler for adding waypoints or isochrone location
    const { setIsochroneLocation } = useAppStore.getState();
    const handleMapClick = (e: maplibregl.MapMouseEvent) => {
      if (ui.mode === 'route') {
        addWaypoint({
          lat: e.lngLat.lat,
          lon: e.lngLat.lng,
        });
      } else if (ui.mode === 'isochrone') {
        setIsochroneLocation({
          lat: e.lngLat.lat,
          lon: e.lngLat.lng,
        });
      }
    };

    map.current.on('click', handleMapClick);

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [ui.mode, addWaypoint]);

  // Update waypoint markers
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    // Add markers for waypoints
    route.waypoints.forEach((waypoint, index) => {
      if (!map.current) return;

      const el = document.createElement('div');
      el.className = 'w-6 h-6 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-xs font-bold';
      
      if (index === 0) {
        el.style.backgroundColor = '#22c55e'; // Green for start
        el.textContent = 'S';
      } else if (index === route.waypoints.length - 1) {
        el.style.backgroundColor = '#ef4444'; // Red for end
        el.textContent = 'E';
      } else {
        el.style.backgroundColor = '#3b82f6'; // Blue for waypoints
        el.textContent = (index + 1).toString();
      }

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([waypoint.lon, waypoint.lat])
        .addTo(map.current);

      markersRef.current.push(marker);
    });
  }, [route.waypoints]);

  // Update route polyline
  useEffect(() => {
    if (!map.current || !route.route?.trip) return;

    const trip: RouteTrip = route.route.trip;
    const sourceId = 'route-source';
    const layerId = 'route-layer';

    // Remove existing route
    if (routeLayerRef.current) {
      if (map.current.getLayer(routeLayerRef.current)) {
        map.current.removeLayer(routeLayerRef.current);
      }
      if (map.current.getSource(routeLayerRef.current)) {
        map.current.removeSource(routeLayerRef.current);
      }
    }

    // Decode route shapes from all legs
    const coordinates: Array<[number, number]> = [];
    trip.legs.forEach((leg) => {
      const decoded = decodePolyline(leg.shape);
      coordinates.push(...decoded);
    });

    if (coordinates.length === 0) return;

    // Add route source
    map.current.addSource(sourceId, {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates,
        },
      },
    });

    // Add route layer
    map.current.addLayer({
      id: layerId,
      type: 'line',
      source: sourceId,
      layout: {
        'line-join': 'round',
        'line-cap': 'round',
      },
      paint: {
        'line-color': '#3b82f6',
        'line-width': 4,
        'line-opacity': 0.8,
      },
    });

    routeLayerRef.current = layerId;

    // Fit bounds to route
    if (coordinates.length > 0) {
      const bounds = coordinates.reduce(
        (bounds, coord) => {
          return bounds.extend(coord as [number, number]);
        },
        new maplibregl.LngLatBounds(coordinates[0] as [number, number], coordinates[0] as [number, number])
      );

      map.current.fitBounds(bounds, {
        padding: { top: 50, bottom: 50, left: 50, right: 50 },
        duration: 1000,
      });
    }

    return () => {
      if (map.current && routeLayerRef.current) {
        if (map.current.getLayer(routeLayerRef.current)) {
          map.current.removeLayer(routeLayerRef.current);
        }
        if (map.current.getSource(routeLayerRef.current)) {
          map.current.removeSource(routeLayerRef.current);
        }
        routeLayerRef.current = null;
      }
    };
  }, [route.route]);

  // Update isochrone polygons
  useEffect(() => {
    if (!map.current || !isochrone.isochrone?.features) return;

    // Remove existing isochrone layers
    isochroneLayersRef.current.forEach((layerId) => {
      if (map.current?.getLayer(layerId)) {
        map.current.removeLayer(layerId);
      }
      if (map.current?.getSource(layerId)) {
        map.current.removeSource(layerId);
      }
    });
    isochroneLayersRef.current = [];

    const colors = ['#3b82f6', '#22c55e', '#eab308', '#f59e0b', '#ef4444'];
    const opacities = [0.3, 0.25, 0.2, 0.15, 0.1];

    // Add isochrone features
    isochrone.isochrone.features.forEach((feature: IsochroneFeature, index) => {
      if (!map.current) return;

      const sourceId = `isochrone-source-${index}`;
      const layerId = `isochrone-layer-${index}`;
      const color = feature.properties.color || colors[index % colors.length];
      const opacity = opacities[index % opacities.length] || 0.3;

      map.current.addSource(sourceId, {
        type: 'geojson',
        data: feature,
      });

      map.current.addLayer({
        id: layerId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': color,
          'fill-opacity': opacity,
        },
      });

      map.current.addLayer({
        id: `${layerId}-outline`,
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': color,
          'line-width': 2,
          'line-opacity': 0.8,
        },
      });

      isochroneLayersRef.current.push(layerId, `${layerId}-outline`);
    });

    // Fit bounds to isochrone if location exists
    if (isochrone.location && isochrone.isochrone.features.length > 0) {
      const feature = isochrone.isochrone.features[0];
      if (feature.geometry.type === 'Polygon' && feature.geometry.coordinates[0]) {
        const coords = feature.geometry.coordinates[0] as Array<[number, number]>;
        const bounds = coords.reduce(
          (bounds, coord) => {
            return bounds.extend(coord);
          },
          new maplibregl.LngLatBounds(coords[0], coords[0])
        );

        map.current.fitBounds(bounds, {
          padding: { top: 50, bottom: 50, left: 50, right: 50 },
          duration: 1000,
        });
      }
    }

    return () => {
      if (map.current) {
        isochroneLayersRef.current.forEach((layerId) => {
          if (map.current?.getLayer(layerId)) {
            map.current.removeLayer(layerId);
          }
          if (map.current?.getSource(layerId)) {
            map.current.removeSource(layerId);
          }
        });
        isochroneLayersRef.current = [];
      }
    };
  }, [isochrone.isochrone, isochrone.location]);

  return (
    <div
      ref={mapContainer}
      className={`w-full h-full ${className || ''}`}
      style={{ minHeight: '400px' }}
    />
  );
});

export default MapComponent;
