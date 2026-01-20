'use client';

import React, { useCallback, useRef, useState } from 'react';
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
import { Upload, Download, Play, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useTrashRoute } from '@/lib/hooks/useTrashRoute';
import type { TrashRouteConfig } from '@/lib/api/trash-route';

export default function TrashCollectionControls() {
  const {
    uploadId,
    jobId,
    uploadStatus,
    jobStatus,
    progress,
    currentStep,
    message,
    error,
    stats,
    uploadFile,
    startGeneration,
    downloadRoute,
    reset,
    isConnected,
  } = useTrashRoute();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [config, setConfig] = useState<TrashRouteConfig>({
    ignore_oneway: true,
    highway_include: ['residential', 'unclassified', 'service', 'tertiary', 'secondary'],
    excluded_conditions: [
      'service=parking_aisle',
      'service=parking',
      'highway=footway',
      'highway=cycleway',
      'highway=steps',
      'highway=path',
      'highway=track',
      'highway=pedestrian',
      'access=private',
    ],
    prefer_right_turns: true,
    turn_cost_multiplier: 1.0,
  });
  const [startNode, setStartNode] = useState<string>('');

  const handleFileSelect = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().match(/\.(osm|xml|pbf)$/)) {
      alert('Please select a valid OSM file (.osm, .xml, or .pbf)');
      return;
    }
    try {
      await uploadFile(file);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  }, [uploadFile]);

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFileSelect(file);
      }
    },
    [handleFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) {
        handleFileSelect(file);
      }
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragging(false);
  }, []);

  const handleGenerate = useCallback(async () => {
    if (!uploadId) {
      alert('Please upload an OSM file first');
      return;
    }

    try {
      const configWithStartNode = {
        ...config,
        start_node: startNode ? parseInt(startNode, 10) : undefined,
      };
      await startGeneration(configWithStartNode);
    } catch (err) {
      console.error('Generation failed:', err);
    }
  }, [uploadId, config, startNode, startGeneration]);

  const handleDownload = useCallback(async () => {
    try {
      await downloadRoute();
    } catch (err) {
      console.error('Download failed:', err);
    }
  }, [downloadRoute]);

  const stepLabels: Record<string, string> = {
    parsing: 'Parsing OSM data',
    building: 'Building road network',
    analyzing: 'Analyzing components',
    solving: 'Solving Eulerian circuit',
    optimizing: 'Optimizing turns',
    writing: 'Writing GPX file',
    complete: 'Complete',
    error: 'Error',
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Trash Collection Route</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* File Upload */}
        <div className="space-y-2">
          <Label>OSM File</Label>
          <div
            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
              dragging
                ? 'border-primary bg-primary/5'
                : uploadStatus === 'success'
                ? 'border-green-500 bg-green-50'
                : 'border-muted-foreground/25 hover:border-primary/50'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".osm,.xml,.pbf"
              onChange={handleFileInputChange}
              className="hidden"
            />
            {uploadStatus === 'idle' && (
              <>
                <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Drag and drop an OSM file here, or click to select
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Supports .osm, .xml, and .pbf formats
                </p>
              </>
            )}
            {uploadStatus === 'uploading' && (
              <>
                <Loader2 className="h-8 w-8 mx-auto mb-2 animate-spin text-primary" />
                <p className="text-sm">Uploading...</p>
              </>
            )}
            {uploadStatus === 'success' && uploadId && (
              <>
                <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <p className="text-sm font-medium">File uploaded successfully</p>
                <p className="text-xs text-muted-foreground mt-1">ID: {uploadId.slice(0, 8)}...</p>
              </>
            )}
            {uploadStatus === 'error' && (
              <>
                <AlertCircle className="h-8 w-8 mx-auto mb-2 text-destructive" />
                <p className="text-sm text-destructive">Upload failed</p>
              </>
            )}
          </div>
        </div>

        {/* Configuration */}
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="config">
            <AccordionTrigger>Configuration</AccordionTrigger>
            <AccordionContent className="space-y-4">
              {/* One-way handling */}
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>One-way Handling</Label>
                  <p className="text-xs text-muted-foreground">
                    {config.ignore_oneway ? 'Option A: Ignore restrictions' : 'Option B: Respect restrictions'}
                  </p>
                </div>
                <Switch
                  checked={config.ignore_oneway}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, ignore_oneway: checked })
                  }
                />
              </div>

              {/* Right-turn preference */}
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Prefer Right Turns</Label>
                  <p className="text-xs text-muted-foreground">Optimize for right turns</p>
                </div>
                <Switch
                  checked={config.prefer_right_turns}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, prefer_right_turns: checked })
                  }
                />
              </div>

              {/* Start node */}
              <div className="space-y-2">
                <Label htmlFor="start-node">Start Node ID (optional)</Label>
                <Input
                  id="start-node"
                  type="number"
                  placeholder="Auto-select"
                  value={startNode}
                  onChange={(e) => setStartNode(e.target.value)}
                />
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        {/* Generate Button */}
        <Button
          onClick={handleGenerate}
          disabled={!uploadId || jobStatus === 'processing' || jobStatus === 'pending'}
          className="w-full"
        >
          {jobStatus === 'processing' || jobStatus === 'pending' ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Play className="mr-2 h-4 w-4" />
              Generate Route
            </>
          )}
        </Button>

        {/* Progress */}
        {(jobStatus === 'processing' || jobStatus === 'pending') && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                {currentStep ? stepLabels[currentStep] : 'Processing...'}
              </span>
              <span className="font-medium">{progress}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            {message && (
              <p className="text-xs text-muted-foreground">{message}</p>
            )}
            {isConnected && (
              <p className="text-xs text-green-600">Connected (real-time updates)</p>
            )}
          </div>
        )}

        {/* Stats */}
        {stats && Object.keys(stats).length > 0 && (
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="stats">
              <AccordionTrigger>Statistics</AccordionTrigger>
              <AccordionContent>
                <dl className="space-y-1 text-sm">
                  {Object.entries(stats).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <dt className="text-muted-foreground capitalize">
                        {key.replace(/_/g, ' ')}:
                      </dt>
                      <dd className="font-medium">{String(value)}</dd>
                    </div>
                  ))}
                </dl>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        )}

        {/* Error */}
        {error && (
          <div className="p-3 bg-destructive/10 border border-destructive rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-destructive mt-0.5" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          </div>
        )}

        {/* Download Button */}
        {jobStatus === 'complete' && (
          <Button onClick={handleDownload} className="w-full" variant="default">
            <Download className="mr-2 h-4 w-4" />
            Download GPX
          </Button>
        )}

        {/* Reset Button */}
        {(uploadId || jobId) && jobStatus !== 'processing' && jobStatus !== 'pending' && (
          <Button onClick={reset} variant="outline" className="w-full">
            Reset
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
