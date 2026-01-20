'use client';

import { useAppStore } from '@/lib/store';
import { useRoute } from '@/lib/hooks/useRoute';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { X, Navigation, Trash2, Download } from 'lucide-react';
import { routeToGPX } from '@/lib/map-utils';
import { metersToKm, secondsToTime } from '@/lib/map-utils';

export default function RouteControls() {
  const { route, clearRoute, removeWaypoint } = useAppStore();
  const { calculateRoute, isLoading, error } = useRoute();
  const waypoints = route?.waypoints || [];

  const handleCalculate = () => {
    if (waypoints.length < 2) {
      return;
    }

    calculateRoute(
      waypoints,
      route.costing,
      route.costingOptions,
      {
        directions_options: {
          units: 'kilometers',
          directions_type: 'instructions',
        },
      }
    );
  };

  const handleExport = () => {
    if (!route.route?.trip) return;

    const trip = route.route.trip;
    const name = `Route from ${waypoints[0].lat.toFixed(4)},${waypoints[0].lon.toFixed(4)}`;
    
    // Decode all route coordinates
    const allCoordinates: Array<[number, number]> = [];
    trip.legs.forEach((leg) => {
      // We need to decode the polyline - for now just use waypoints
      // In a real implementation, decode the shape polyline
      allCoordinates.push([leg.summary.min_lon, leg.summary.min_lat]);
      allCoordinates.push([leg.summary.max_lon, leg.summary.max_lat]);
    });

    // Use waypoints as fallback
    if (allCoordinates.length === 0) {
      waypoints.forEach((wp) => {
        allCoordinates.push([wp.lon, wp.lat]);
      });
    }

    const gpx = routeToGPX(name, allCoordinates);
    const blob = new Blob([gpx], { type: 'application/gpx+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'route.gpx';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Waypoints</span>
            <span className="text-sm font-normal text-muted-foreground">
              {waypoints.length}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {waypoints.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-4">
              Click on the map to add waypoints
            </p>
          )}

          {waypoints.map((waypoint, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 border rounded-md"
            >
              <div className="flex items-center gap-2">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                    index === 0
                      ? 'bg-green-500'
                      : index === waypoints.length - 1
                      ? 'bg-red-500'
                      : 'bg-blue-500'
                  }`}
                >
                  {index === 0
                    ? 'S'
                    : index === waypoints.length - 1
                    ? 'E'
                    : index + 1}
                </div>
                <div className="text-sm">
                  <div className="font-medium">
                    {index === 0
                      ? 'Start'
                      : index === waypoints.length - 1
                      ? 'End'
                      : `Waypoint ${index + 1}`}
                  </div>
                  <div className="text-muted-foreground text-xs">
                    {waypoint.lat.toFixed(4)}, {waypoint.lon.toFixed(4)}
                  </div>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeWaypoint(index)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}

          {waypoints.length >= 2 && (
            <div className="flex gap-2 pt-2">
              <Button
                onClick={handleCalculate}
                disabled={isLoading || waypoints.length < 2}
                className="flex-1"
              >
                <Navigation className="h-4 w-4 mr-2" />
                {isLoading ? 'Calculating...' : 'Calculate Route'}
              </Button>
              {waypoints.length > 0 && (
                <Button
                  variant="outline"
                  onClick={clearRoute}
                  disabled={isLoading}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {route.route?.trip && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Route Summary</span>
              <Button variant="ghost" size="icon" onClick={handleExport}>
                <Download className="h-4 w-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">Distance</div>
                <div className="text-lg font-semibold">
                  {metersToKm(route.route.trip.summary.length).toFixed(2)} km
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Time</div>
                <div className="text-lg font-semibold">
                  {secondsToTime(route.route.trip.summary.time)}
                </div>
              </div>
            </div>
            <div className="pt-2 border-t">
              <div className="text-sm text-muted-foreground">Maneuvers</div>
              <div className="text-lg font-semibold">
                {route.route.trip.legs.reduce(
                  (acc, leg) => acc + leg.maneuvers.length,
                  0
                )}
              </div>
            </div>
            {route.route.trip.summary.has_toll && (
              <div className="pt-2 text-sm text-amber-600">
                ⚠️ Route includes tolls
              </div>
            )}
            {route.route.trip.summary.has_ferry && (
              <div className="pt-2 text-sm text-blue-600">
                ⛴️ Route includes ferry
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
