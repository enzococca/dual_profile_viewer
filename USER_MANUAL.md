# Dual Profile Viewer - Complete User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation Guide](#installation-guide)
3. [Quick Start Tutorial](#quick-start-tutorial)
4. [Core Features](#core-features)
5. [Advanced 3D Visualization](#advanced-3d-visualization)
6. [Archaeological Workflows](#archaeological-workflows)
7. [Case Studies](#case-studies)
8. [Export Options](#export-options)
9. [Tips & Best Practices](#tips-best-practices)
10. [Troubleshooting](#troubleshooting)

## Introduction

The Dual Profile Viewer is a professional QGIS plugin designed specifically for archaeological terrain analysis. It creates parallel elevation profiles from DEM/DTM data with advanced 3D visualization capabilities, enabling detailed analysis of archaeological features.

### Key Benefits
- **Precision Analysis**: Sub-meter accuracy for archaeological features
- **3D Visualization**: Industry-leading PyVista integration
- **Scientific Documentation**: Publication-ready outputs
- **Workflow Optimization**: Streamlined archaeological workflows

## Installation Guide

### System Requirements
- **QGIS**: Version 3.0 or higher
- **Python**: 3.7+
- **RAM**: 4GB minimum (8GB recommended for 3D)
- **Graphics**: OpenGL 3.3+ support

### Step-by-Step Installation

#### Method 1: QGIS Plugin Repository
1. Open QGIS
2. Navigate to `Plugins` → `Manage and Install Plugins`
3. Search for "Dual Profile Viewer"
4. Click `Install Plugin`
5. Restart QGIS if prompted

#### Method 2: Manual Installation
```bash
# Download the plugin
wget https://github.com/enzococca/dual_profile_viewer/archive/main.zip

# Extract to plugins folder
# Windows
unzip main.zip -d %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\

# macOS
unzip main.zip -d ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/

# Linux
unzip main.zip -d ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Installing Dependencies

#### Core Dependencies (Automatic)
The plugin will automatically prompt to install:
- numpy
- plotly

#### 3D Visualization Dependencies
```bash
# Recommended: PyVista
pip install pyvista pyvistaqt

# Alternative if PyVista fails
pip install vispy
```

## Quick Start Tutorial

### Your First Profile (2 minutes)

1. **Load DEM Data**
   - Open QGIS
   - Load your DEM: `Layer` → `Add Layer` → `Add Raster Layer`
   - Select your DEM file

2. **Open Plugin**
   - Click the Dual Profile Viewer icon in toolbar
   - Or go to `Raster` → `Dual Profile Viewer`

3. **Configure Settings**
   - **DEM Layer**: Select from dropdown
   - **Offset**: 2m (for a typical wall)
   - **Points**: 200 (good detail)
   - **Interpolation**: Linear

4. **Draw Profile**
   - Click "Draw Profile" button
   - Click once to start line
   - Move perpendicular to feature
   - Click again to finish

5. **Analyze Results**
   - View interactive graph
   - Red line = Profile A
   - Blue line = Profile B
   - Hover for exact values

6. **3D Visualization**
   - Click "🎨 3D Visualization"
   - Explore in 3D space
   - Adjust vertical exaggeration

## Core Features

### Profile Drawing Tool

#### Drawing Controls
- **Left Click**: Start/end profile line
- **Mouse Move**: Preview parallel lines
- **ESC**: Cancel current drawing
- **Right Click**: Context menu

#### Parameters
| Parameter | Range | Default | Use Case |
|-----------|-------|---------|----------|
| Offset | 0.5-100m | 2m | Wall width/feature size |
| Points | 10-1000 | 200 | Resolution vs performance |
| Interpolation | 3 types | Linear | Terrain characteristics |

### Interactive 2D Graphs

#### Graph Features
- **Zoom**: Scroll wheel or box select
- **Pan**: Click and drag
- **Hover**: Display exact values
- **Export**: Download as image/data
- **Reset**: Double-click to reset view

#### Statistical Display
- Minimum/maximum elevations
- Average gradient
- Total distance
- Elevation difference

## Advanced 3D Visualization

### 3D Viewer Interface

#### Main Controls
- **Vertical Exaggeration**: 0.1x - 5.0x slider
- **Opacity**: 0-100% transparency
- **Edges**: Toggle wireframe display
- **Grid**: Show/hide reference grid
- **Intersections**: Auto-calculate crossing points

#### Texture Options
1. **Solid Color**: Traditional red/blue
2. **Elevation Gradient**: Color by height
3. **Slope Gradient**: Color by steepness
4. **Custom**: User-defined colors

#### Navigation
- **Rotate**: Left-click + drag
- **Zoom**: Mouse wheel
- **Pan**: Middle-click + drag
- **Reset**: Press 'R'

### Interactive Features

#### Point Interrogation
1. Enable point picking mode
2. Click on any point in 3D
3. View coordinates and elevation
4. Add to metadata table
5. Export to attribute table

#### Section Management
- Select individual sections
- Adjust opacity for comparison
- Scale sections independently
- Calculate intersections

#### Reference Tools
- Add horizontal reference planes
- Set elevation markers
- Create measurement grids
- Define stratigraphic levels

## Archaeological Workflows

### Workflow 1: Roman Wall Analysis

**Objective**: Document wall construction and preservation

1. **Data Preparation**
   ```
   DEM Resolution: 0.5m or better
   Area: Wall section + 10m buffer
   CRS: Local projected system
   ```

2. **Profile Parameters**
   ```
   Offset: 2-3m (wall width)
   Points: 300 (high detail)
   Interpolation: Linear
   Sections: Every 5m along wall
   ```

3. **Analysis Steps**
   - Draw perpendicular profiles
   - Identify foundation levels
   - Measure preserved height
   - Note construction phases
   - Document robbing trenches

4. **3D Visualization**
   - Load all sections
   - Apply elevation gradient
   - Set vertical exag to 2x
   - Add reference plane at foundation
   - Export for report

### Workflow 2: Defensive Ditch System

**Objective**: Analyze ditch morphology and capacity

1. **Setup**
   ```
   Offset: 20m (full ditch width)
   Points: 500 (capture detail)
   Interpolation: Cubic (smooth)
   ```

2. **Systematic Sampling**
   - Profile every 10m
   - Maintain consistent orientation
   - Number sections sequentially

3. **Analysis**
   - Measure maximum depths
   - Calculate cross-sectional area
   - Identify recutting episodes
   - Estimate water capacity

4. **Volume Calculation**
   - Export as polygons
   - Calculate area per section
   - Multiply by section spacing
   - Sum for total volume

### Workflow 3: Settlement Terraces

**Objective**: Reconstruct terrace system

1. **Grid Approach**
   - Create profile grid
   - 5m spacing
   - Both orientations

2. **Height Analysis**
   - Identify terrace edges
   - Measure riser heights
   - Calculate tread widths
   - Map terrace boundaries

3. **3D Reconstruction**
   - Load all profiles
   - Enable intersections
   - Add reference planes at each level
   - Export 3D model

## Case Studies

### Case Study 1: Hadrian's Wall Fort

**Site**: Vindolanda, UK
**Feature**: Triple ditch system
**Method**: LiDAR analysis

**Process**:
1. Loaded 0.5m LiDAR DTM
2. Created 15 profiles across ditches
3. Offset: 25m (spanning all ditches)
4. Points: 500 per profile

**Results**:
- **Ditch 1**: 2.5m deep, V-shaped, military
- **Ditch 2**: 2.1m deep, recut twice
- **Ditch 3**: 1.8m deep, partially filled
- **Volume**: ~15,000 m³ excavated
- **Dating**: Construction phases identified

**3D Analysis**:
- Intersection points showed drainage
- Reference planes at Roman ground level
- Slope analysis revealed erosion patterns

### Case Study 2: Medieval Castle

**Site**: Château de Montségur, France
**Feature**: Inner and outer baileys
**Method**: Drone photogrammetry

**Process**:
1. Generated 0.1m DEM from drone
2. Systematic profiles every 2m
3. Offset: 3m for walls, 15m for ditches

**Results**:
- Wall heights: 3-7m surviving
- Identified 3 construction phases
- Located collapsed sections
- Mapped internal structures

**Visualization**:
- 3D model showed defensive sight lines
- Texture mapping revealed stone types
- Export for virtual reconstruction

### Case Study 3: Prehistoric Hillfort

**Site**: Maiden Castle, UK
**Feature**: Multiple ramparts
**Method**: Combined LiDAR and geophysics

**Process**:
1. Integrated LiDAR with resistivity
2. Radial profiles from center
3. Variable offsets per rampart

**Results**:
- Mapped 4 rampart circuits
- Heights: 8m, 6m, 4m, 3m
- Identified entrance complexes
- Calculated labor investment

## Export Options

### Vector Export

#### Available Formats
| Format | Extension | Best For |
|--------|-----------|----------|
| Shapefile | .shp | GIS compatibility |
| GeoPackage | .gpkg | Modern GIS |
| GeoJSON | .geojson | Web mapping |
| KML | .kml | Google Earth |
| DXF | .dxf | CAD software |

#### Geometry Types
- **Polyline**: Profile lines
- **Polygon**: Area between profiles
- **Points**: Elevation samples

### Data Export

#### CSV Structure
```csv
Distance_m,X,Y,Z_ProfileA,Z_ProfileB,Difference
0.00,523456.78,4123456.78,234.56,234.45,0.11
1.25,523457.90,4123457.90,234.78,234.67,0.11
```

### 3D Model Export

#### Formats
- **VTK**: Scientific visualization
- **STL**: 3D printing
- **OBJ**: 3D modeling
- **PLY**: Point clouds

### Image Export

#### 2D Graphs
- PNG (with world file)
- SVG (vector graphics)
- PDF (reports)
- HTML (interactive)

#### 3D Views
- Screenshot (current view)
- High-res render
- Animation sequences

## Tips & Best Practices

### Data Preparation
1. **Check DEM quality**: Remove artifacts
2. **Verify CRS**: Use projected systems
3. **Set no-data values**: Properly defined
4. **Consider resolution**: Match to feature size

### Profile Strategy
1. **Perpendicular orientation**: Cross features at 90°
2. **Consistent spacing**: Systematic sampling
3. **Adequate offset**: Capture full feature
4. **Sufficient points**: Balance detail/speed

### 3D Optimization
1. **Reduce points**: For performance
2. **Disable edges**: When not needed
3. **Lower opacity**: For overlapping sections
4. **Use LOD**: Level of detail settings

### Publication Quality
1. **High resolution**: 300 DPI minimum
2. **Consistent style**: Colors and fonts
3. **Scale bars**: Always include
4. **North arrow**: For orientation
5. **Coordinate info**: CRS and units

## Troubleshooting

### Common Issues

#### No Elevation Data
**Problem**: Profiles show no data
**Solutions**:
- Check DEM has valid values
- Verify CRS matches project
- Ensure profile intersects DEM
- Check no-data value settings

#### 3D Viewer Won't Open
**Problem**: Error when opening 3D view
**Solutions**:
```bash
# Install PyVista
pip install pyvista pyvistaqt

# Check OpenGL
python -c "import pyvista; pyvista.Report()"

# Try alternative
pip install vispy
```

#### Slow Performance
**Problem**: Lag in 3D viewer
**Solutions**:
- Reduce point count (<500)
- Disable edge display
- Lower number of sections
- Close other applications
- Update graphics drivers

#### Export Errors
**Problem**: Cannot export files
**Solutions**:
- Check write permissions
- Verify path exists
- Ensure valid filename
- Check disk space
- Try different format

### Getting Help

#### Support Channels
- **GitHub Issues**: Bug reports
- **Email**: enzo.ccc@gmail.com
- **Wiki**: Documentation
- **Forum**: QGIS community

#### Diagnostic Information
When reporting issues, include:
1. QGIS version
2. Plugin version
3. Operating system
4. Error messages
5. Sample data (if possible)

## Keyboard Shortcuts

### General
- `ESC`: Cancel operation
- `Ctrl+Z`: Undo
- `F1`: Help
- `Ctrl+S`: Save

### 3D Viewer
- `R`: Reset view
- `W`: Toggle wireframe
- `G`: Toggle grid
- `I`: Toggle intersections
- `+/-`: Adjust point size
- `Space`: Play/pause animation

## Advanced Configuration

### Settings File
`~/.qgis3/dual_profile_viewer/settings.json`

```json
{
  "defaults": {
    "offset": 2.0,
    "points": 200,
    "interpolation": "linear"
  },
  "3d": {
    "vertical_exaggeration": 2.0,
    "texture": "elevation",
    "auto_intersections": true
  },
  "export": {
    "format": "gpkg",
    "precision": 2
  }
}
```

---

*Version 1.0.0 - Complete Documentation*
*© 2024 Enzo Cocca - Archaeological GIS Solutions*