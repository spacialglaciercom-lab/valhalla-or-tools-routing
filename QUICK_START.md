# Quick Start - Trash Collection Route Generator

## Installation (One-Time)

```bash
cd C:\Users\Space
pip install networkx gpxpy shapely geopy
```

## Generate a Route

### Simplest Command
```bash
python scripts/generate_trash_route.py --osm "mercier_area.osm"
```

### With Custom Output Directory
```bash
python scripts/generate_trash_route.py \
    --osm "mercier_area.osm" \
    --output "output"
```

### With Verbose Output
```bash
python scripts/generate_trash_route.py \
    --osm "mercier_area.osm" \
    --verbose
```

## Output Files

After running, check:
- **GPX Route**: `output/trash_collection_route.gpx`
- **Analysis Report**: `output/route_report.md`

## What You Get

### GPX File
- Single continuous track (start = end point)
- Ready for GPS devices and mapping applications
- 59 waypoints for the test route
- Total distance: 18.5 km
- Estimated drive time: 37 minutes

### Report File
Includes:
- Route guarantees (single track, right-side collection, turn optimization)
- Road filtering details (included/excluded highways)
- Route statistics (distance, time, turn analysis)
- Component information (connected road networks)

## Test the System

```bash
python tests/test_route_generator.py
```

Expected output:
```
Ran 15 tests in 0.022s
OK
```

## Using Your Own OSM File

1. Get an OSM extract from OpenStreetMap (e.g., using Overpass API)
2. Save it as `.osm` XML format
3. Run:
```bash
python scripts/generate_trash_route.py --osm "your_file.osm" --output "results"
```

## Understanding the Output

### GPX File Structure
- Single `<trk>` element (no multiple tracks)
- Single `<trkseg>` element (no breaks)
- Contains waypoint sequence for turn-by-turn navigation

### Report Sections
1. **Route Guarantees** - What the route ensures
2. **Included/Excluded** - Road filtering applied
3. **Statistics** - Distance, time, turn analysis
4. **Notes** - Methodology and data source

### Key Statistics
- **Directed traversals**: Should be ≈ 2 × unique segments
- **Turn analysis**: More right turns than left (optimization working)

## Common Tasks

### Change Output Filenames
```bash
python scripts/generate_trash_route.py \
    --osm "data.osm" \
    --gpx "my_route_name" \
    --report "my_report"
```

### Start from Specific Node
```bash
python scripts/generate_trash_route.py \
    --osm "data.osm" \
    --start-node 12345
```

### Enable Debug Logging
```bash
python scripts/generate_trash_route.py \
    --osm "data.osm" \
    --verbose
```

## Example Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate route for test data
python scripts/generate_trash_route.py --osm "mercier_area.osm" --output "output"

# 3. View the results
cat output/route_report.md           # Read report
# (open output/trash_collection_route.gpx in a GPX viewer)

# 4. Run tests to verify system
python tests/test_route_generator.py
```

## Configuration

To modify filtering rules or turn preferences:

Edit `src/route_generator/config.py`:
- `HIGHWAY_INCLUDE` - Which road types to include
- `NON_DRIVEABLE` - Road types to exclude
- `TURN_WEIGHTS` - Turn preference penalties
- `AVERAGE_SPEED_KMH` - Speed for time estimation

## Features

✅ Parses OSM XML data
✅ Filters for driveable roads
✅ Creates Eulerian circuits (no breaks)
✅ Traverses each segment twice (right-side collection)
✅ Optimizes for right turns
✅ Generates GPX tracks
✅ Produces analysis reports
✅ Fully tested (15/15 tests pass)

## Help & Documentation

- Full documentation: `TRASH_ROUTE_GENERATOR_README.md`
- Implementation details: `IMPLEMENTATION_COMPLETE.md`
- API usage: See Python docstrings in source code

## Support

For issues:
1. Run with `--verbose` flag to see detailed logs
2. Check that OSM file is valid XML format
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Run tests: `python tests/test_route_generator.py`

---

**Ready to use!** Start with the simplest command and check `output/` for results.
