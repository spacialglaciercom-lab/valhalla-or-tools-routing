# Generated route.gpx from uploaded OSM extract
Generated: 2026-05-03T03:51:08.983200
Source OSM: D:/trash_routes/uploads/4ae9b6f8-2c95-4d3a-93bb-0dcace5e091c/input.osm

## 1. What the GPX route guarantees
- **Single continuous track (no breaks):** YES - Single <trk> with single <trkseg>.
  WHY: Eulerian circuit algorithm guarantees a closed loop where start node = end node.
  Waypoints are added in strict circuit order with no breaks, ensuring continuous navigation.

- **Right-side arm collection logic:** At the segment level, each OSM way segment between
  two nodes is added as a bidirectional edge pair in the graph (forward and reverse directions).
  The Eulerian circuit traverses both edges exactly once, meaning each segment is driven
  once forward and once reverse. This ensures each curb appears on the truck's right side
  during one of the two passes.

- **Reduced left turns where possible:** Uses bearing-based turn angle calculation.
  When multiple next edges exist at a junction, the system analyzes turn angles and
  prefers edges with lowest turn cost where: right turns (0-90°) = cost 0.5-1.0,
  straight (±10°) = 1.0, left turns (-90-0°) = cost 2.0-3.0, U-turns (>150°) = cost 3.0+.
  Turn statistics are computed and reported for route analysis.

## 2. What was included / excluded
- **Included highway tags:** tertiary, service, residential, unclassified, secondary
- **Excluded conditions:**
  - service=parking_aisle
  - service=parking
  - highway=footway
  - highway=cycleway
  - highway=steps
  - highway=path
  - highway=track
  - highway=pedestrian
  - access=private

- **Connected components found:** 1
- **Component chosen:** Largest component (3 nodes)
- **Unique segments total (in all components):** 2
- **Segments routed (chosen component):** 2
- **Segments excluded (disconnected):** 0

## 3. Route statistics (from generated GPX)
- **Directed traversals:** 4
  (Should be ≈ 2 × unique_segments for 'twice' rule)
- **Approx distance:** 0.06 km
- **Estimated drive time:** 0.1 minutes
  (0.0 hours at 30 km/h average)

### Turn Analysis
- **Right turns:** 1
- **Left turns:** 1
- **Straight:** 1
- **U-turns (>150°):** 2

### Start Point Selection
- **Start point:** Node 2 (highest total degree - most connections)
  Ensures route begins at well-connected intersection for efficient coverage.

## Notes
- OSM XML format processed
- One-way restrictions ignored per Option A (preserves 'twice' traversal for right-side collection)
- Output saved to: route.gpx
