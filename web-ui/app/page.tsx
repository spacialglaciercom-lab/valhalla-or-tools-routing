'use client';

import React, { useEffect } from 'react';
import dynamic from 'next/dynamic';
import Sidebar from './components/Sidebar';
import RouteControls from './components/RouteControls';
import IsochroneControls from './components/IsochroneControls';
import TrashCollectionControls from './components/TrashCollectionControls';
import TrashRouteVisualizer from './components/TrashRouteVisualizer';
import JsonViewer from './components/JsonViewer';
import { useAppStore } from '@/lib/store';
import { getStatus } from '@/lib/valhalla';
import { Button } from './components/ui/button';
import { Card, CardContent } from './components/ui/card';

// Dynamically import Map to avoid SSR issues with MapLibre GL
const Map = dynamic(() => import('./components/Map'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-muted">
      <div className="text-muted-foreground">Loading map...</div>
    </div>
  ),
});

export default function Home() {
  const { ui, route, isochrone } = useAppStore();
  const [connectionStatus, setConnectionStatus] = React.useState<{
    connected: boolean;
    message: string;
  }>({ connected: false, message: 'Checking...' });

  useEffect(() => {
    // Check Valhalla connection on mount
    getStatus()
      .then(() => {
        setConnectionStatus({ connected: true, message: 'Connected to Valhalla' });
      })
      .catch((error) => {
        setConnectionStatus({
          connected: false,
          message: `Connection failed: ${error.message}`,
        });
      });
  }, []);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />

      <main
        className={`flex-1 flex flex-col transition-all duration-300 ${
          ui.sidebarOpen ? 'ml-80' : 'ml-0'
        }`}
      >
        <div className="h-full relative">
          <Map className="w-full h-full" />

          {/* Connection Status */}
          {!connectionStatus.connected && (
            <div className="absolute top-4 left-4 z-10">
              <Card className="border-destructive bg-background/95 backdrop-blur">
                <CardContent className="p-3">
                  <p className="text-sm text-destructive font-medium">
                    {connectionStatus.message}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Make sure Valhalla is running on port 8002
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Controls Panel */}
          <div className="absolute top-4 right-4 z-10 w-96 max-h-[80vh] overflow-y-auto">
            {ui.mode === 'route' && <RouteControls />}
            {ui.mode === 'isochrone' && <IsochroneControls />}
            {ui.mode === 'trash-collection' && <TrashCollectionControls />}
            {ui.mode === 'matrix' && (
              <Card>
                <CardContent className="p-4">
                  <p className="text-sm text-muted-foreground">
                    Matrix mode coming soon
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Loading Overlay */}
          {(route.isLoading || isochrone.isLoading) && (
            <div className="absolute inset-0 bg-background/50 backdrop-blur-sm flex items-center justify-center z-20">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                    <div>
                      <p className="font-medium">Calculating...</p>
                      <p className="text-sm text-muted-foreground">
                        {route.isLoading
                          ? 'Computing route'
                          : 'Computing isochrone'}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Trash Route Visualizer */}
          {ui.mode === 'trash-collection' && <TrashRouteVisualizer />}
        </div>
      </main>

      <JsonViewer />
    </div>
  );
}
