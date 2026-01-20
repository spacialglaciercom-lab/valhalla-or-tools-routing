'use client';

import { useState } from 'react';
import { useAppStore } from '@/lib/store';
import { useIsochrone } from '@/lib/hooks/useIsochrone';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { X, Navigation, Plus, Trash2 } from 'lucide-react';
import type { Location } from '@/types/valhalla';

const CONTOUR_COLORS = [
  '#3b82f6',
  '#22c55e',
  '#eab308',
  '#f59e0b',
  '#ef4444',
];

export default function IsochroneControls() {
  const { isochrone, setIsochroneLocation, setContours, clearIsochrone } = useAppStore();
  const { calculateIsochrone, isLoading, error } = useIsochrone();

  const [timeInputs, setTimeInputs] = useState<number[]>([15]);

  const handleAddContour = () => {
    const newTime = timeInputs[timeInputs.length - 1] + 5 || 5;
    setTimeInputs([...timeInputs, newTime]);
    setContours([
      ...isochrone.contours,
      {
        time: newTime,
        color: CONTOUR_COLORS[timeInputs.length % CONTOUR_COLORS.length],
      },
    ]);
  };

  const handleRemoveContour = (index: number) => {
    const newTimes = timeInputs.filter((_, i) => i !== index);
    const newContours = isochrone.contours.filter((_, i) => i !== index);
    setTimeInputs(newTimes);
    setContours(newContours);
  };

  const handleTimeChange = (index: number, value: number) => {
    const newTimes = [...timeInputs];
    newTimes[index] = value;
    setTimeInputs(newTimes);

    const newContours = [...isochrone.contours];
    newContours[index] = {
      ...newContours[index],
      time: value,
    };
    setContours(newContours);
  };

  const handleCalculate = () => {
    if (!isochrone.location) {
      return;
    }

    if (isochrone.contours.length === 0) {
      return;
    }

    calculateIsochrone(
      isochrone.location,
      isochrone.contours,
      isochrone.costing,
      isochrone.costingOptions,
      {
        polygons: true,
        denoise: 1.0,
        generalize: 200.0,
      }
    );
  };

  const handleLocationClick = () => {
    // In a real implementation, you might want to use map click or geocoder
    // For now, we'll use a default location or let the user input coordinates
    if (!isochrone.location) {
      // Default to San Francisco
      setIsochroneLocation({
        lat: 37.7749,
        lon: -122.4194,
      });
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Isochrone Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Location</Label>
            {isochrone.location ? (
              <div className="p-2 border rounded-md flex items-center justify-between">
                <div className="text-sm">
                  <div className="font-medium">Selected Location</div>
                  <div className="text-muted-foreground text-xs">
                    {isochrone.location.lat.toFixed(4)},{' '}
                    {isochrone.location.lon.toFixed(4)}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsochroneLocation(null)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <div className="p-4 border-2 border-dashed rounded-md text-center">
                <p className="text-sm text-muted-foreground mb-2">
                  Click on the map to set location
                </p>
                <Button variant="outline" size="sm" onClick={handleLocationClick}>
                  Use Default Location
                </Button>
              </div>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Time Contours (minutes)</Label>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleAddContour}
                disabled={isochrone.contours.length >= 5}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>

            {isochrone.contours.map((contour, index) => (
              <div
                key={index}
                className="flex items-center gap-2 p-2 border rounded-md"
              >
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: contour.color || CONTOUR_COLORS[index] }}
                />
                <Input
                  type="number"
                  value={timeInputs[index] || contour.time || 15}
                  onChange={(e) =>
                    handleTimeChange(index, parseInt(e.target.value) || 15)
                  }
                  min="1"
                  max="120"
                  className="flex-1"
                />
                <span className="text-sm text-muted-foreground">min</span>
                {isochrone.contours.length > 1 && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleRemoveContour(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-2 pt-2">
            <Button
              onClick={handleCalculate}
              disabled={isLoading || !isochrone.location || isochrone.contours.length === 0}
              className="flex-1"
            >
              <Navigation className="h-4 w-4 mr-2" />
              {isLoading ? 'Calculating...' : 'Calculate Isochrone'}
            </Button>
            {isochrone.location && (
              <Button variant="outline" onClick={clearIsochrone} disabled={isLoading}>
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {isochrone.isochrone && (
        <Card>
          <CardHeader>
            <CardTitle>Isochrone Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground">
              {isochrone.isochrone.features.length} contour
              {isochrone.isochrone.features.length !== 1 ? 's' : ''} generated
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
