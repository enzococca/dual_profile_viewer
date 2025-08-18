# Dual Profile Viewer - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Interface Overview](#interface-overview)
4. [Step-by-Step Tutorial](#step-by-step-tutorial)
5. [Advanced Features](#advanced-features)
6. [Use Cases](#use-cases)
7. [Tips and Best Practices](#tips-and-best-practices)
8. [FAQ](#faq)

## Introduction

The Dual Profile Viewer is a specialized QGIS plugin designed for archaeological and geological analysis. It creates two parallel elevation profiles from Digital Elevation Models (DEM) or Digital Terrain Models (DTM), allowing for detailed analysis of terrain features, archaeological structures, and landscape characteristics.

### Key Concepts

- **Profile Line**: The central line you draw on the map
- **Offset Distance**: The perpendicular distance from the central line to each parallel profile
- **Elevation Profile**: A graph showing elevation changes along a line
- **Dual Profiles**: Two parallel profiles that help analyze features like walls, ditches, or terraces

## Getting Started

### Prerequisites

1. QGIS 3.0 or higher installed
2. At least one DEM/DTM raster layer loaded in your project
3. Basic familiarity with QGIS interface

### First Steps

1. **Load Your Data**:
   ```
   Project → Open → Select your project with DEM data
   OR
   Layer → Add Layer → Add Raster Layer → Select your DEM file
   ```

2. **Open the Plugin**:
   - Click the Dual Profile Viewer icon in the toolbar
   - Or navigate to: Raster → Dual Profile Viewer

## Interface Overview

### Main Dialog Components

1. **Raster Selection**
   - Dropdown menu listing all raster layers in your project
   - Multi-DEM comparison checkbox

2. **Profile Parameters**
   - Offset Distance: Distance between parallel profiles (in map units)
   - Sample Interval: Distance between elevation samples

3. **Action Buttons**
   - Draw Profile: Activates the drawing tool
   - Clear Profiles: Removes current profiles
   - Export Options: Various export formats

4. **Visualization Area**
   - Interactive graph showing elevation profiles
   - Statistics panel with min/max/mean values

## Step-by-Step Tutorial

### Creating Your First Dual Profile

1. **Prepare Your Workspace**
   - Load your DEM/DTM layer
   - Zoom to your area of interest
   - Ensure the DEM covers the area you want to analyze

2. **Configure Profile Settings**
   - Select your DEM from the dropdown
   - Set offset distance (e.g., 5 meters for analyzing a 10m wide structure)
   - Leave sample interval at default (1.0) for standard resolution

3. **Draw the Profile Line**
   - Click "Draw Profile" button
   - Click on the map to set the start point
   - Move your mouse to see the preview lines
   - Click again to set the end point

4. **Analyze the Results**
   - The graph will automatically appear
   - Red line: Profile 1 (left side)
   - Blue line: Profile 2 (right side)
   - Gray dashed line: Center line (optional)

5. **Interact with the Graph**
   - Hover over points to see exact elevation values
   - Click and drag to zoom in
   - Double-click to reset zoom
   - Use toolbar buttons for pan/zoom modes

### Exporting Your Results

#### As Vector Layers

1. Click "Export as Vector"
2. Choose export type:
   - **Polyline**: Simple line following the elevation profile
   - **Polygon**: Filled area from baseline to profile
   - **3D Polyline**: Line with actual elevation values

3. Set scaling options:
   - Vertical Exaggeration: Enhance elevation differences (default: 1.0)
   - Overall Scale: Scale the entire profile (default: 1.0)

4. Choose output format and location
5. Click "Export"

#### As Data (CSV)

1. Click "Export as CSV"
2. Choose save location
3. The CSV will contain:
   - Distance along profile
   - Elevation values for both profiles
   - Coordinate information

#### As Image (PNG)

1. Click "Export as PNG"
2. Choose save location
3. Automatically creates:
   - PNG image of the graph
   - World file (.pgw) for georeferencing

## Advanced Features

### Multi-DEM Comparison

Perfect for comparing different temporal datasets or data sources:

1. Check "Enable multi-DEM comparison"
2. Select additional DEM layers
3. Each DEM will show different colored profiles
4. Legend indicates which line corresponds to which DEM

### Custom Styling

When exporting as vector:
- Profiles are automatically styled with appropriate colors
- Labels are added at regular intervals
- Customize further using QGIS styling tools

### 3D Visualization

Export as 3D polyline and view in QGIS 3D view:
1. Export with "3D Polyline" option
2. Open 3D map view in QGIS
3. Your profile maintains real-world elevations

## Use Cases

### Archaeological Applications

1. **Wall Analysis**
   - Set offset to wall width
   - Profiles show both sides of the wall
   - Identify construction phases through elevation differences

2. **Ditch/Moat Survey**
   - Profile across the feature
   - Analyze depth and slope angles
   - Compare filled vs. original profiles

3. **Terrace Mapping**
   - Profile perpendicular to terrace edges
   - Measure terrace heights and widths
   - Identify agricultural or defensive terraces

### Geological Applications

1. **Fault Analysis**
   - Profile across suspected fault lines
   - Identify vertical displacement
   - Measure fault scarps

2. **River Valley Profiles**
   - Analyze valley cross-sections
   - Identify terraces and floodplains
   - Study erosion patterns

## Tips and Best Practices

### Optimal Settings

1. **Offset Distance**
   - For walls: Use actual wall width
   - For general analysis: Start with 10-20% of feature width
   - For regional profiles: Use larger offsets (50-100m)

2. **Sample Interval**
   - High-resolution DEM (1m): Use 1.0
   - Medium-resolution (5-10m): Use 2.0-5.0
   - Low-resolution (30m+): Use 10.0+

3. **Profile Length**
   - Extend profiles beyond features of interest
   - Include context on both sides
   - Consider terrain constraints

### Quality Checks

1. Verify DEM coverage before drawing
2. Check for NoData values in results
3. Compare with field observations
4. Use hillshade as background for visual verification

## FAQ

**Q: Why don't I see any profiles after drawing?**
A: Check that:
- Your DEM layer is selected
- The profile line intersects the DEM extent
- The DEM has valid elevation values (not all NoData)

**Q: Can I save my profile lines for later?**
A: Yes, export as vector layers. They maintain all spatial information and can be reloaded.

**Q: How do I compare historical DEMs?**
A: Use the multi-DEM comparison feature. Load all historical DEMs, then enable comparison mode.

**Q: The elevation values seem wrong?**
A: Check:
- DEM units (meters vs feet)
- Vertical datum
- NoData value handling

**Q: Can I edit the profile after creation?**
A: You need to draw a new profile. Save important profiles as vectors for permanent storage.

**Q: How do I report elevation differences?**
A: The statistics panel shows min/max/mean for each profile. Export to CSV for detailed analysis.

## Keyboard Shortcuts

- `Esc`: Cancel current drawing operation
- `Space`: Toggle between pan and draw mode (when drawing)
- `Delete`: Clear current profiles

## Getting Help

- **Issues**: Report bugs on [GitHub](https://github.com/enzococca/dual-profile-viewer/issues)
- **Questions**: Email enzo.ccc@gmail.com
- **Updates**: Check the plugin repository for new versions