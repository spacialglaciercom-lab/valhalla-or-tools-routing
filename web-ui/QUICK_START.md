# Valhalla Web UI - Quick Start Guide

## Prerequisites

- Node.js 18+ installed
- npm or yarn installed
- Docker and Docker Compose installed
- Valhalla backend running (via Docker)

## Step 1: Start Valhalla Backend

Open PowerShell/Terminal and navigate to the Valhalla Docker directory:

```powershell
cd C:\Users\Space\valhalla-docker
docker-compose up -d
```

Wait for the service to start (this may take 1-2 minutes). Verify it's running:

```powershell
curl http://localhost:8002/status
```

You should see a JSON response indicating the service is running.

## Step 2: Install Frontend Dependencies

Navigate to the web-ui directory:

```powershell
cd C:\Users\Space\web-ui
```

Install all npm packages:

```powershell
npm install
```

This will install all required dependencies (Next.js, React, MapLibre GL JS, etc.). This may take 2-5 minutes depending on your internet connection.

**If you encounter npm install errors:**
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json` if they exist
- Retry: `npm install`

## Step 3: Configure Environment (Optional)

The application defaults to `http://localhost:8002` for the Valhalla backend. If your Valhalla instance is running on a different URL, create a `.env.local` file:

```powershell
cd C:\Users\Space\web-ui
echo NEXT_PUBLIC_VALHALLA_URL=http://localhost:8002 > .env.local
```

Or manually create `.env.local` with:
```
NEXT_PUBLIC_VALHALLA_URL=http://localhost:8002
```

## Step 4: Start Development Server

In the web-ui directory, run:

```powershell
npm run dev
```

You should see output indicating Next.js is starting:
```
✔ Ready in X.Xs
- Local:        http://localhost:3000
```

## Step 5: Open in Browser

Open your web browser and navigate to:
```
http://localhost:3000
```

The Valhalla Routing Web Interface should load.

## Step 6: Using the Application

### Route Planning:
1. Click "Route" mode in the sidebar (if not already selected)
2. Select a costing profile (Auto, Bicycle, Pedestrian, or Truck) from the sidebar
3. Click on the map to add waypoints (green marker = start, blue = waypoints, red = end)
4. Click "Calculate Route" button when you have at least 2 waypoints
5. View the route summary (distance, time, maneuvers)
6. Optionally export the route as GPX using the download icon

### Isochrone Generation:
1. Click "Isochrone" mode in the sidebar
2. Click on the map to set the starting location
3. Configure time contours (e.g., 5, 10, 15 minutes)
4. Click "Calculate Isochrone" to generate polygons
5. View overlapping polygons with different opacities on the map

### View JSON Request/Response:
1. Click the JSON button in the bottom-right corner
2. View the raw request sent to Valhalla API
3. View the raw response received from Valhalla API
4. Use the copy buttons to copy JSON to clipboard

## Troubleshooting

### Cannot connect to Valhalla:
- Verify Valhalla is running: `curl http://localhost:8002/status`
- Check Docker container: `docker-compose ps` (in valhalla-docker directory)
- Check Docker logs: `docker-compose logs valhalla`

### Map not loading:
- Check browser console for errors (F12)
- Verify internet connection (map tiles load from OpenStreetMap)
- Try refreshing the page

### npm install fails:
- Ensure Node.js 18+ is installed: `node --version`
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then retry
- Try using `npm install --legacy-peer-deps` if peer dependency errors occur

### Port 3000 already in use:
- Stop other applications using port 3000
- Or specify a different port: `npm run dev -- -p 3001`

## Stopping the Application

To stop the development server:
- Press `Ctrl+C` in the terminal where `npm run dev` is running

To stop Valhalla backend:
```powershell
cd C:\Users\Space\valhalla-docker
docker-compose down
```

## Next Steps

- Explore different costing profiles and their options
- Try generating isochrones with multiple time intervals
- Export routes as GPX files for use in other applications
- View the JSON request/response to understand the Valhalla API format
