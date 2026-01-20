'use client';

import { useAppStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { X, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import JsonView from '@uiw/react-json-view';

export default function JsonViewer() {
  const { ui, setJsonViewerOpen, toggleJsonViewer } = useAppStore();
  const [copied, setCopied] = useState<'request' | 'response' | null>(null);

  const handleCopy = (type: 'request' | 'response') => {
    const data = type === 'request' ? ui.lastRequest : ui.lastResponse;
    if (data) {
      navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    }
  };

  if (!ui.jsonViewerOpen) {
    return (
      <Button
        onClick={toggleJsonViewer}
        variant="outline"
        size="icon"
        className="fixed bottom-4 right-4 z-50"
      >
        <X className="h-4 w-4" />
      </Button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-[800px] max-h-[600px] bg-background border border-border rounded-lg shadow-lg z-50 flex flex-col">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h3 className="text-lg font-semibold">JSON Request/Response</h3>
        <Button onClick={toggleJsonViewer} variant="ghost" size="icon">
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-hidden grid grid-cols-2">
        <div className="border-r border-border overflow-auto p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium">Request</h4>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleCopy('request')}
              className="h-6 w-6"
            >
              {copied === 'request' ? (
                <Check className="h-3 w-3" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          </div>
          {ui.lastRequest ? (
            <JsonView
              value={ui.lastRequest}
              style={{
                backgroundColor: 'transparent',
                fontSize: '12px',
              }}
              collapsed={2}
              displayObjectSize={false}
              displayDataTypes={false}
            />
          ) : (
            <p className="text-sm text-muted-foreground">No request data</p>
          )}
        </div>

        <div className="overflow-auto p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium">Response</h4>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleCopy('response')}
              className="h-6 w-6"
            >
              {copied === 'response' ? (
                <Check className="h-3 w-3" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          </div>
          {ui.lastResponse ? (
            <JsonView
              value={ui.lastResponse}
              style={{
                backgroundColor: 'transparent',
                fontSize: '12px',
              }}
              collapsed={2}
              displayObjectSize={false}
              displayDataTypes={false}
            />
          ) : (
            <p className="text-sm text-muted-foreground">No response data</p>
          )}
        </div>
      </div>
    </div>
  );
}
