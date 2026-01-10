# Desktop GUI Application

## Overview

User-friendly desktop application for generating trash collection routes. No command-line knowledge required!

## Running the GUI

### Option 1: Run Python Script
```bash
python gui/trash_route_gui.py
```

### Option 2: Run Standalone Executable
Double-click `TrashRouteGenerator.exe` (after packaging)

## Features

- **Easy File Selection**: Browse button to select OSM files
- **Output Folder Selection**: Choose where to save results
- **Custom Filenames**: Set custom names for GPX and report files
- **Progress Display**: Real-time status updates during generation
- **Result Viewing**: One-click buttons to view generated files
- **Error Handling**: User-friendly error messages

## Usage

1. Click "Browse..." next to "OSM File" and select your .osm or .xml file
2. (Optional) Click "Browse..." next to "Output Folder" to change output location
3. (Optional) Change GPX and Report filenames
4. Click "Generate Route" button
5. Wait for generation to complete
6. View results in the text area
7. Click buttons to open output folder, view GPX, or view report

## System Requirements

- Windows 10 or later (for executable)
- Python 3.8+ (if running from source)

## Troubleshooting

**Problem**: "Please select a valid OSM file"
- **Solution**: Make sure you've selected an .osm or .xml file

**Problem**: "Cannot create output directory"
- **Solution**: Check that you have write permissions to the selected folder

**Problem**: Generation takes a long time
- **Solution**: Large OSM files (>10MB) may take several minutes. Progress is shown in status area.
