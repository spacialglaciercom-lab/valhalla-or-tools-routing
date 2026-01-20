# Valhalla Routing Engine - Web Interface

Modern, high-performance web interface for the Valhalla Routing Engine built with Next.js 14, MapLibre GL JS, and Tailwind CSS.

## Features

- **Interactive Map**: MapLibre GL JS map with OpenStreetMap tiles
- **Route Planning**: Click on map to add waypoints, calculate routes with multiple costing profiles
- **Isochrone Visualization**: Generate isochrones with multiple time contours and overlapping polygons
- **Costing Configuration**: Dynamic sidebar with options for auto, bicycle, pedestrian, and truck profiles
- **JSON Viewer**: Side-by-side view of request/response JSON with syntax highlighting
- **Export Routes**: Download routes as GPX files
- **Responsive Design**: Modern UI with Tailwind CSS and Shadcn components

## Prerequisites

- Node.js 18+ and npm/yarn
- Valhalla routing engine running (default: `http://localhost:8002`)
- Docker setup for Valhalla (see `../valhalla-docker/`)

## Quick Start

1. **Install Dependencies**

```bash
cd web-ui
npm install
```

2. **Configure Environment**

Copy `.env.local.example` to `.env.local` and update if needed:

```bash
cp .env.local.example .env.local
```

The default configuration assumes Valhalla is running on `http://localhost:8002`.

3. **Start Valhalla Backend**

Ensure your Valhalla Docker service is running:

```bash
cd ../valhalla-docker
docker-compose up -d
```

Check status:
```bash
curl http://localhost:8002/status
```

4. **Run Development Server**

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

### Route Planning

1. Select **Route** mode from the sidebar
2. Choose a costing profile (auto, bicycle, pedestrian, truck)
3. Click on the map to add waypoints (green = start, blue = waypoints, red = end)
4. Click **Calculate Route** to compute the route
5. View route summary (distance, time, maneuvers)
6. Export route as GPX if needed

### Isochrone Generation

1. Select **Isochrone** mode from the sidebar
2. Click on map to set location (or use default location)
3. Configure time contours (e.g., 5, 10, 15 minutes)
4. Click **Calculate Isochrone** to generate polygons
5. View overlapping polygons with different opacities

### Costing Options

Each costing profile has specific options accessible via accordion in the sidebar:

- **Auto**: Use highways, tolls, ferry options, height restrictions
- **Bicycle**: Bicycle type (Road, Cross, Hybrid, Mountain), use roads/tracks/hills
- **Pedestrian**: Walking speed, path preferences
- **Truck**: Height, width, weight restrictions, highway preferences

### JSON Viewer

Toggle the JSON viewer (bottom-right button) to see the raw request and response JSON sent to/received from the Valhalla API. Useful for debugging and understanding the API format.

## Project Structure

```
web-ui/
├── app/
│   ├── components/          # React components
│   │   ├── Map.tsx          # MapLibre GL JS map component
│   │   ├── Sidebar.tsx      # Costing configuration sidebar
│   │   ├── RouteControls.tsx # Route input controls
│   │   ├── IsochroneControls.tsx # Isochrone configuration
│   │   ├── JsonViewer.tsx   # JSON request/response viewer
│   │   └── ui/              # Shadcn UI components
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main page
│   └── globals.css          # Global styles
├── lib/
│   ├── valhalla.ts          # Valhalla API client
│   ├── store.ts             # Zustand state management
│   ├── map-utils.ts         # Map utility functions
│   ├── utils.ts             # General utilities
│   └── hooks/               # Custom React hooks
│       ├── useRoute.ts      # Route fetching hook
│       ├── useIsochrone.ts  # Isochrone fetching hook
│       └── useMatrix.ts     # Matrix calculation hook
├── types/
│   └── valhalla.ts          # TypeScript type definitions
└── public/                  # Static assets
```

## API Integration

The application communicates directly with the Valhalla backend:

- **Route**: `POST /route` - Calculate route between waypoints
- **Isochrone**: `POST /isochrone` - Generate isochrone polygons
- **Matrix**: `POST /sources_to_targets` - Calculate distance/time matrix
- **Status**: `GET /status` - Check backend health

See [Valhalla API Documentation](https://valhalla.github.io/valhalla/api/) for full API reference.

## Configuration

### Valhalla Backend URL

Set `NEXT_PUBLIC_VALHALLA_URL` in `.env.local`:

```env
NEXT_PUBLIC_VALHALLA_URL=http://localhost:8002
```

### Map Tile Source

By default, the app uses OpenStreetMap tiles. To use a different tile source, modify `app/components/Map.tsx`.

## Performance Optimization

- **Memoization**: Map component and route calculations are memoized
- **Dynamic Imports**: Map component is dynamically imported to avoid SSR issues
- **Debouncing**: Map interactions are debounced for better performance
- **Lazy Loading**: Large components are lazy-loaded

## Building for Production

```bash
npm run build
npm start
```

The production build will be optimized and can be deployed to Vercel, Netlify, or any Node.js hosting service.

## Troubleshooting

### Map Not Loading

- Check browser console for errors
- Ensure MapLibre GL CSS is imported correctly
- Verify network connectivity to tile servers

### Cannot Connect to Valhalla

- Verify Valhalla is running: `curl http://localhost:8002/status`
- Check `NEXT_PUBLIC_VALHALLA_URL` in `.env.local`
- Ensure CORS is configured if Valhalla is on a different domain

### Route Calculation Fails

- Check Valhalla logs: `docker-compose logs valhalla`
- Verify waypoints are in valid geographic bounds
- Ensure Valhalla tiles are loaded correctly

## License

This project follows the same license as Valhalla (MIT License).
