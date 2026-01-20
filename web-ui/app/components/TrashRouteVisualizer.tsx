'use client';

import React from 'react';
import { useTrashRoute } from '@/lib/hooks/useTrashRoute';
import { Card, CardContent } from './ui/card';

/**
 * TrashRouteVisualizer displays route statistics overlay on the map.
 * Future enhancement: Parse and visualize GPX route on MapLibre map
 */
export default function TrashRouteVisualizer() {
  const { stats, jobStatus } = useTrashRoute();

  if (jobStatus !== 'complete' || !stats) {
    return null;
  }

  // Extract route statistics from stats object
  const routeStats = stats.route_stats || stats.summary || stats;
  const routeInfo = routeStats as Record<string, unknown> | undefined;

  return (
    <div className="absolute bottom-4 left-4 z-10 max-w-sm">
      <Card>
        <CardContent className="p-4">
          <h3 className="font-semibold mb-2">Route Statistics</h3>
          {routeInfo && (
            <dl className="space-y-1 text-sm">
              {routeInfo.total_distance_km !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Distance:</dt>
                  <dd className="font-medium">{String(routeInfo.total_distance_km)} km</dd>
                </div>
              )}
              {routeInfo.estimated_drive_time_minutes !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Est. Time:</dt>
                  <dd className="font-medium">{String(routeInfo.estimated_drive_time_minutes)} min</dd>
                </div>
              )}
              {routeInfo.circuit_length !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Circuit Length:</dt>
                  <dd className="font-medium">{String(routeInfo.circuit_length)} edges</dd>
                </div>
              )}
              {routeInfo.nodes_parsed !== undefined && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Nodes:</dt>
                  <dd className="font-medium">{String(routeInfo.nodes_parsed)}</dd>
                </div>
              )}
            </dl>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
