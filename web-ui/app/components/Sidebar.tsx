'use client';

import { useState } from 'react';
import { useAppStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Switch } from './ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from './ui/accordion';
import { Menu, X } from 'lucide-react';
import type { CostingType, CostingOptions } from '@/types/valhalla';

export default function Sidebar() {
  const {
    ui,
    route,
    isochrone,
    setMode,
    setCosting,
    setCostingOptions,
    setIsochroneCosting,
    setIsochroneCostingOptions,
    setSidebarOpen,
    toggleSidebar,
  } = useAppStore();

  const currentMode = ui.mode;
  const currentCosting = currentMode === 'route' ? route.costing : isochrone.costing;
  const currentCostingOptions =
    currentMode === 'route' ? route.costingOptions : isochrone.costingOptions;

  const handleCostingChange = (costing: CostingType) => {
    if (currentMode === 'route') {
      setCosting(costing);
    } else {
      setIsochroneCosting(costing);
    }
  };

  const handleCostingOptionChange = (key: string, value: unknown) => {
    const newOptions: CostingOptions = {
      ...currentCostingOptions,
      [currentCosting]: {
        ...((currentCostingOptions[currentCosting as keyof CostingOptions] as Record<string, unknown>) || {}),
        [key]: value,
      },
    };

    if (currentMode === 'route') {
      setCostingOptions(newOptions);
    } else {
      setIsochroneCostingOptions(newOptions);
    }
  };

  const renderCostingOptions = () => {
    const options = (currentCostingOptions[currentCosting as keyof CostingOptions] as Record<string, unknown>) || {};

    if (currentCosting === 'auto') {
      return (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="auto-options">
            <AccordionTrigger>Auto Options</AccordionTrigger>
            <AccordionContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="use-highways">Use Highways</Label>
                <Switch
                  id="use-highways"
                  checked={options.use_highways !== 0.0}
                  onCheckedChange={(checked) =>
                    handleCostingOptionChange('use_highways', checked ? 1.0 : 0.0)
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="use-tolls">Use Tolls</Label>
                <Switch
                  id="use-tolls"
                  checked={options.use_tolls !== 0.0}
                  onCheckedChange={(checked) =>
                    handleCostingOptionChange('use_tolls', checked ? 1.0 : 0.0)
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="use-ferry">Use Ferry</Label>
                <Switch
                  id="use-ferry"
                  checked={options.use_ferry !== 0.0}
                  onCheckedChange={(checked) =>
                    handleCostingOptionChange('use_ferry', checked ? 1.0 : 0.0)
                  }
                />
              </div>
              {typeof options.height === 'number' && (
                <div className="space-y-2">
                  <Label htmlFor="height">Height (m)</Label>
                  <Input
                    id="height"
                    type="number"
                    value={options.height}
                    onChange={(e) =>
                      handleCostingOptionChange('height', parseFloat(e.target.value) || 0)
                    }
                  />
                </div>
              )}
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      );
    }

    if (currentCosting === 'bicycle') {
      return (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="bicycle-options">
            <AccordionTrigger>Bicycle Options</AccordionTrigger>
            <AccordionContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="bicycle-type">Bicycle Type</Label>
                <Select
                  value={(options.bicycle_type as string) || 'Road'}
                  onValueChange={(value) => handleCostingOptionChange('bicycle_type', value)}
                >
                  <SelectTrigger id="bicycle-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Road">Road</SelectItem>
                    <SelectItem value="Cross">Cross</SelectItem>
                    <SelectItem value="Hybrid">Hybrid</SelectItem>
                    <SelectItem value="Mountain">Mountain</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="use-roads">Use Roads</Label>
                <Switch
                  id="use-roads"
                  checked={options.use_roads !== 0.0}
                  onCheckedChange={(checked) =>
                    handleCostingOptionChange('use_roads', checked ? 1.0 : 0.0)
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="use-tracks">Use Tracks</Label>
                <Switch
                  id="use-tracks"
                  checked={options.use_tracks !== 0.0}
                  onCheckedChange={(checked) =>
                    handleCostingOptionChange('use_tracks', checked ? 1.0 : 0.0)
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <Label htmlFor="use-hills">Use Hills</Label>
                <Switch
                  id="use-hills"
                  checked={options.use_hills !== 0.0}
                  onCheckedChange={(checked) =>
                    handleCostingOptionChange('use_hills', checked ? 1.0 : 0.0)
                  }
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      );
    }

    if (currentCosting === 'pedestrian') {
      return (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="pedestrian-options">
            <AccordionTrigger>Pedestrian Options</AccordionTrigger>
            <AccordionContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="walking-speed">Walking Speed (km/h)</Label>
                <Input
                  id="walking-speed"
                  type="number"
                  value={(options.walking_speed as number) || 5.1}
                  onChange={(e) =>
                    handleCostingOptionChange('walking_speed', parseFloat(e.target.value) || 5.1)
                  }
                  step="0.1"
                  min="1"
                  max="10"
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      );
    }

    if (currentCosting === 'truck') {
      return (
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="truck-options">
            <AccordionTrigger>Truck Options</AccordionTrigger>
            <AccordionContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="truck-use-highways">Use Highways</Label>
                <Switch
                  id="truck-use-highways"
                  checked={options.use_highways !== 0.0}
                  onCheckedChange={(checked) =>
                    handleCostingOptionChange('use_highways', checked ? 1.0 : 0.0)
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="truck-height">Height (m)</Label>
                <Input
                  id="truck-height"
                  type="number"
                  value={(options.height as number) || 4.0}
                  onChange={(e) =>
                    handleCostingOptionChange('height', parseFloat(e.target.value) || 4.0)
                  }
                  step="0.1"
                  min="0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="truck-width">Width (m)</Label>
                <Input
                  id="truck-width"
                  type="number"
                  value={(options.width as number) || 2.6}
                  onChange={(e) =>
                    handleCostingOptionChange('width', parseFloat(e.target.value) || 2.6)
                  }
                  step="0.1"
                  min="0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="truck-weight">Weight (kg)</Label>
                <Input
                  id="truck-weight"
                  type="number"
                  value={(options.weight as number) || 0}
                  onChange={(e) =>
                    handleCostingOptionChange('weight', parseFloat(e.target.value) || 0)
                  }
                  min="0"
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      );
    }

    return null;
  };

  if (!ui.sidebarOpen) {
    return (
      <Button
        onClick={toggleSidebar}
        variant="outline"
        size="icon"
        className="fixed top-4 left-4 z-50"
      >
        <Menu className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <div className="w-80 bg-background border-r border-border h-screen overflow-y-auto fixed left-0 top-0 z-40">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h2 className="text-lg font-semibold">Valhalla Routing</h2>
        <Button onClick={toggleSidebar} variant="ghost" size="icon">
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="p-4 space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Mode</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant={currentMode === 'route' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setMode('route')}
              >
                Route
              </Button>
              <Button
                variant={currentMode === 'isochrone' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setMode('isochrone')}
              >
                Isochrone
              </Button>
              <Button
                variant={currentMode === 'trash-collection' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setMode('trash-collection')}
                className="col-span-2"
              >
                Trash Collection
              </Button>
              <Button
                variant={currentMode === 'matrix' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setMode('matrix')}
                disabled
                className="col-span-2"
              >
                Matrix
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Costing Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="costing">Profile</Label>
              <Select value={currentCosting} onValueChange={handleCostingChange}>
                <SelectTrigger id="costing">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto</SelectItem>
                  <SelectItem value="bicycle">Bicycle</SelectItem>
                  <SelectItem value="pedestrian">Pedestrian</SelectItem>
                  <SelectItem value="truck">Truck</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {renderCostingOptions()}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
