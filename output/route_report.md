# Generated trash_collection_route.gpx from uploaded OSM extract
Generated: 2026-01-09T23:56:48.660738
Source OSM: C:\Users\Space\mercier_area.osm

## 1. What the GPX route guarantees
- **Single continuous track (no breaks):** YES - Single <trk> with single <trkseg>
- **Right-side arm collection logic:** Each street segment driven twice (both directions)
  so each curb appears on truck's right side on one of the two passes.
- **Reduced left turns where possible:** Greedy heuristic applied to prefer right turns,
  penalize left turns and U-turns using bearing-based turn angle calculation.
- **One-way street handling:** IGNORED - Route may violate one-way restrictions to satisfy
  'traverse twice' requirement for right-side collection.

## 2. What was included / excluded
- **Included highway tags:** service, unclassified, residential, secondary, tertiary
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
- **Component chosen:** Largest component (20 nodes)
- **Unique segments (in all components):** Unknown (see component sizes)
- **Segments routed (chosen component):** 29
- **Segments excluded (disconnected):** 0 nodes

## 3. Route statistics (from generated GPX)
- **Directed traversals:** 58
  (Should be ≈ 2 × unique_segments for 'twice' rule)
- **Approx distance:** 18.5 km
- **Estimated drive time:** 37.0 minutes
  (0.62 hours at 30 km/h average)

### Turn Analysis
- **Right turns:** 26
- **Left turns:** 22
- **Straight:** 9
- **U-turns (>150°):** 20

## Notes
- OSM XML format extracted for Mercier area (bounds: 45.304-45.316 lat, -73.742 to -73.726 lon)
- One-way restrictions ignored per Option A (preserves 'twice' traversal)
- Output saved to: trash_collection_route.gpx
