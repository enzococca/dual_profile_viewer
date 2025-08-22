# Dual Profile Viewer - Complete User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation Guide](#installation-guide)
3. [Quick Start](#quick-start)
4. [Interface Overview](#interface-overview)
5. [Drawing Profiles](#drawing-profiles)
6. [Perpendicular Sections](#perpendicular-sections)
7. [Visualization Features](#visualization-features)
8. [Multi-DEM Analysis](#multi-dem-analysis)
9. [Export and Output](#export-and-output)
10. [Advanced Features](#advanced-features)
11. [Troubleshooting](#troubleshooting)
12. [Frequently Asked Questions](#frequently-asked-questions)

## Introduction

The Dual Profile Viewer is a comprehensive QGIS plugin for advanced elevation profile analysis. It offers single/dual profile modes, polygon multi-section support, 3D visualization, and professional output capabilities.

### Key Capabilities
- **Profile Modes**: Single, dual parallel, and polygon multi-section
- **3D Visualization**: PyVista and Plotly integration
- **Multi-DEM Support**: Compare multiple elevation models
- **Professional Output**: Layouts, vector export, AI reports
- **Real-time Preview**: See profiles while drawing

## Installation Guide

### Prerequisites
- QGIS 3.16 or higher
- Python 3.7+
- 4GB RAM minimum (8GB for 3D features)
- OpenGL support for 3D visualization

### Installation Methods

#### Via QGIS Plugin Manager (Recommended)
1. Open QGIS
2. Go to `Plugins` → `Manage and Install Plugins`
3. Search for "Dual Profile Viewer"
4. Click `Install Plugin`
5. Restart QGIS if prompted

#### Manual Installation
```bash
# Clone or download the plugin
git clone https://github.com/yourusername/dual_profile_viewer.git

# Copy to QGIS plugins directory
# Windows
copy dual_profile_viewer "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\"

# macOS
cp -r dual_profile_viewer ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/

# Linux
cp -r dual_profile_viewer ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Installing Dependencies

#### Required (Auto-installed)
```bash
pip install numpy matplotlib plotly
```

#### Optional for 3D Features
```bash
# PyVista for advanced 3D
pip install pyvista vtk

# For AI reports
pip install requests
```

## Quick Start

### Basic Workflow (5 minutes)

1. **Load Data**
   - Add DEM/DTM raster to QGIS
   - Ensure proper CRS is set

2. **Open Plugin**
   - Click toolbar icon or
   - Menu: `Plugins` → `Dual Profile Viewer`

3. **Select DEM**
   - Choose from dropdown
   - Verify selection shows elevation range

4. **Draw Profile**
   - Click drawing mode button
   - Click start and end points on map
   - View generated profile

5. **Analyze**
   - Examine 2D plot
   - Open 3D viewer
   - Export results

## Interface Overview

### Main Window Components

#### Top Toolbar
- **DEM Selector**: Dropdown list of loaded rasters
- **Refresh**: Update DEM list
- **Browse**: Add multiple DEMs for comparison

#### Drawing Controls
- **Draw Section**: Standard dual profile mode
- **Single Section**: Individual profile only
- **Polygon Section**: Multi-section from polygon

#### Parameters Panel
- **Offset Distance**: Space between parallel profiles (0.5-1000m)
- **Sample Points**: Profile resolution (50-1000)
- **Interpolation**: Linear or cubic

#### Visualization Tabs
- **Plot**: 2D elevation graphs
- **3D View**: Terrain visualization
- **Statistics**: Numerical analysis
- **Report**: AI-generated insights

#### Action Buttons
- **Clear**: Remove current profiles
- **Export**: Save as vector/image
- **Layout**: Generate print layout
- **Statistics**: View detailed metrics

## Drawing Profiles

### Single Section Mode

Perfect for simple transects:

1. **Activate**: Click `Single Section` button
2. **Draw**: 
   - First click: Start point
   - Move mouse: See preview line
   - Second click: End point
3. **Result**: Single elevation profile displayed

**Use Cases**:
- Quick elevation checks
- Simple cross-sections
- Path profiles

### Dual Section Mode (Default)

Ideal for feature analysis:

1. **Set Parameters**:
   - Offset distance (e.g., 2m for walls)
   - Sample points (200 default)

2. **Draw Main Line**:
   - Click start point
   - Preview shows both lines
   - Click end point

3. **Automatic Generation**:
   - A-A' (red): Main profile
   - B-B' (blue): Parallel profile
   - Both displayed in plot

**Use Cases**:
- Wall analysis
- Ditch profiles
- Road sections

### Polygon Multi-Section Mode

For comprehensive area analysis:

1. **Activate**: Click `Polygon Section`
2. **Draw Polygon**:
   - Click vertices sequentially
   - Right-click to complete
3. **Automatic Processing**:
   - One profile per side
   - All sections numbered
   - Combined visualization

**Features**:
- Supports any polygon shape
- Color-coded sections
- Intersection analysis in 3D

**Use Cases**:
- Building foundations
- Fortification analysis
- Area surveys

### Drawing Tips

#### Precision Drawing
- Use snapping for accuracy
- Zoom in for detail
- Hold Shift for straight lines

#### Real-time Feedback
- Preview shows while drawing
- Offset updates dynamically
- Elevation shown at cursor

## Perpendicular Sections

### Overview
The perpendicular sections feature allows you to create cross-sectional profiles perpendicular to your main profile line. This is particularly useful for analyzing terrain variations across your main section.

### Creating Perpendicular Sections

#### Step-by-Step Process
1. **Create Main Profile**:
   - Draw your main section using any mode
   - Generate the profile by clicking "Create"

2. **Activate Interactive Marker**:
   - Press the 'X' key on your keyboard
   - The marker turns green when active
   - A red marker indicates inactive state

3. **Position the Marker**:
   - Move your mouse along the section line
   - The marker follows your cursor position
   - A vertical line shows the current position on the graph

4. **Create Perpendicular**:
   - Right-click at desired position
   - Enter the perpendicular length (in meters)
   - Click OK to create the section

5. **View Results**:
   - A new tab appears with the perpendicular profile
   - Green dashed lines on main profile show intersection points
   - Each perpendicular is numbered sequentially

### Features and Options

#### Interactive Marker
- **Visual Feedback**: Green when active, red when inactive
- **Precise Positioning**: Follows mouse movement exactly
- **Toggle Control**: Press X to activate/deactivate

#### Perpendicular Properties
- **Variable Length**: Set different lengths for each perpendicular
- **Automatic Orientation**: Always 90° to main profile
- **Multiple Sections**: Create unlimited perpendiculars

#### Visualization
- **Separate Tabs**: Each perpendicular in its own tab
- **Navigation Toolbar**: Zoom, pan, and save options
- **Intersection Markers**: Green dashed lines on main profile

### Working with Perpendicular Data

#### Creating Layers
1. Click "Create Layer" button after creating perpendiculars
2. A progress dialog shows layer creation status
3. Perpendicular sections appear as green lines on map
4. Layer named "Perpendicular_Sections" added to project

#### Export Options
- **Vector Export**: Includes all perpendicular sections
- **Layout Generation**: Each perpendicular gets its own page
- **Image Export**: Use toolbar save button for individual plots

### Best Practices

#### Planning Perpendiculars
- Consider terrain features when positioning
- Use consistent lengths for comparative analysis
- Create perpendiculars at regular intervals for systematic sampling

#### Performance Tips
- Create all perpendiculars before generating layers
- Use reasonable lengths (avoid extremely long sections)
- Close unused tabs to free memory

## Visualization Features

### 2D Profile Plots

#### Matplotlib View
- **Static Plot**: High-quality rendering
- **Navigation Toolbar**: Added for all plots
  - Zoom and pan controls
  - Home button to reset view
  - Save button for direct image export
- **Features**:
  - Grid toggle
  - Axis scaling
  - Export to image
- **Best For**: Reports, printing

#### Plotly Interactive
- **Dynamic Plot**: Browser-based
- **Features**:
  - Zoom/pan
  - Hover details
  - Data export
- **Best For**: Exploration, sharing

#### Plot Controls
- **Y-Axis**: Fixed or adaptive
- **Grid**: Show/hide
- **Legend**: Toggle visibility
- **Export**: PNG, SVG, HTML

### 3D Visualization

#### PyVista 3D Viewer

**Opening**:
1. Click `3D View (PyVista)` button
2. Wait for initialization
3. Interact with scene

**Controls**:
- **Rotate**: Left mouse drag
- **Zoom**: Right mouse or scroll
- **Pan**: Middle mouse drag
- **Reset**: Press 'r'

**Features**:
- Terrain mesh with profiles
- Intersection highlighting
- Vertical exaggeration
- Multiple texture options

**Display Options**:
- **Surface**: Smooth terrain
- **Wireframe**: Mesh view
- **Points**: Vertex display
- **Edges**: Show/hide

#### Plotly 3D Web Viewer

**Advantages**:
- No additional dependencies
- Shareable HTML output
- Works in any browser

**Features**:
- Interactive rotation
- Elevation coloring
- Profile lines overlay
- Export capabilities

### Visualization Settings

#### Color Schemes
- Elevation gradients
- Slope-based coloring
- Custom palettes
- Categorical schemes

#### Scaling Options
- Vertical exaggeration (0.5-5x)
- Horizontal scaling
- Aspect ratio lock
- Auto-scaling

## Multi-DEM Analysis

### Adding Multiple DEMs

1. **Browse for DEMs**:
   - Click `Browse` button
   - Select multiple files
   - Supported: GeoTIFF, ASCII, IMG

2. **Manage List**:
   - View selected DEMs
   - Remove unwanted
   - Set primary DEM

3. **Profile Extraction**:
   - Automatic from all DEMs
   - Same sample locations
   - Synchronized display

### Comparison Features

#### Side-by-Side Plots
- Each DEM in subplot
- Synchronized axes
- Difference calculation
- Statistics per DEM

#### Overlay Mode
- All profiles on one plot
- Color-coded by DEM
- Legend with sources
- Direct comparison

#### Applications
- Temporal analysis
- Resolution comparison
- Error assessment
- Data validation

## Export and Output

### Vector Export

#### Profile as Polyline
- **Format**: 3D line geometry
- **Attributes**: Elevation, distance
- **Use**: GIS analysis, CAD

#### Profile as Polygon
- **Format**: Filled area geometry
- **Attributes**: Area, volume
- **Use**: Volume calculations

#### 3D Vector Export
- **Format**: True 3D coordinates
- **Attributes**: X, Y, Z values
- **Use**: 3D GIS, modeling

#### Export Process
1. Click `Export` button
2. Choose export type
3. Set parameters:
   - Vertical exaggeration
   - Scale factor
   - Output format
4. Save to file
5. Add to map (optional)

### Layout Generation

#### Automated Layouts

**Single Section**:
- A4/A3 page size
- Profile plot (left)
- Location map (right)
- Statistics table
- Scale bar

**Multi-Section**:
- One page per section
- Consistent formatting
- Section overview map
- Combined statistics

#### Layout Customization
- Page size and orientation
- Element positioning
- Colors and fonts
- Logo/text addition

#### Export Options
- PDF (vector quality)
- PNG/JPEG (raster)
- SVG (editable)
- Print directly

### Statistics Export

#### Available Metrics
- **Elevation**: Min, max, mean, std dev
- **Distance**: Total length, sampling
- **Slope**: Average, maximum, distribution
- **Volume**: Cut/fill estimates

#### Export Formats
- Text file (.txt)
- CSV spreadsheet
- Clipboard copy
- Direct to report

### AI Report Generation

#### Setup
1. Click `AI Report` button
2. Choose service:
   - OpenAI GPT-4
   - Anthropic Claude
3. Enter API key (saved)

#### Report Options
- Statistical analysis
- Geological interpretation
- Archaeological insights
- Recommendations

#### Output
- Formatted text
- HTML report
- PDF export
- Layout integration

## Advanced Features

### Batch Processing

Process multiple profiles automatically:

```python
# Example script
profiles = []
for i in range(0, 1000, 50):
    start = QgsPointXY(x + i, y)
    end = QgsPointXY(x + i, y + 1000)
    profile = viewer.extract_profile(start, end)
    profiles.append(profile)
```

### Custom Symbology

#### Single Sections
- Simple red line
- Adjustable width
- Transparency control

#### Dual Sections
- Red (A-A'): Primary
- Blue (B-B'): Secondary
- Labeled automatically

#### Multi-Sections
- Rainbow color scheme
- Numbered sequentially
- Legend included

### Integration Features

#### QGIS Processing
- Available in toolbox
- Batch processing
- Model builder compatible

#### Python API
```python
# Access from console
from dual_profile_viewer import DualProfileViewer
viewer = DualProfileViewer()
viewer.extract_profile(layer, start, end)
```

#### Attribute Table
- Link to features
- Store profile data
- Update dynamically

## Troubleshooting

### Common Issues

#### PyVista Won't Install
```bash
# Try conda instead
conda install -c conda-forge pyvista

# Or specific versions
pip install pyvista==0.38.0 vtk==9.2.0
```

#### No Elevation Data
**Check**:
- DEM coverage area
- CRS compatibility
- No-data values
- Raster validity

**Fix**:
- Reproject if needed
- Set no-data value
- Clip to area

#### 3D Viewer Crashes
**Causes**:
- GPU driver issues
- Memory limitations
- VTK conflicts

**Solutions**:
- Update graphics drivers
- Reduce point density
- Use Plotly instead

#### Export Fails
**Check**:
- Write permissions
- Disk space
- Valid data
- Format support

### Performance Optimization

#### Large Datasets
- Reduce sample points
- Use pyramids/overviews
- Limit 3D complexity
- Close unused viewers

#### Multiple Profiles
- Process in batches
- Use memory efficiently
- Clear old data
- Optimize rendering

#### System Resources
- Monitor RAM usage
- GPU acceleration
- Multiprocessing
- Cache management

## Frequently Asked Questions

### General Usage

**Q: What DEM formats are supported?**
A: All GDAL raster formats including GeoTIFF, ASCII Grid, IMG, HGT, etc.

**Q: Can I use multiple CRS?**
A: Yes, automatic reprojection is handled by QGIS.

**Q: Maximum profile length?**
A: No hard limit, but performance decreases beyond 50km.

### Features

**Q: Can I edit profiles after creation?**
A: No, but you can redraw with different parameters.

**Q: Is batch processing possible?**
A: Yes, through Python scripting or Processing toolbox.

**Q: Can I save my settings?**
A: Settings are saved per QGIS project.

### Technical

**Q: Required Python version?**
A: Python 3.7 or higher (QGIS 3.16+).

**Q: GPU requirements for 3D?**
A: OpenGL 3.3+ support, 2GB VRAM recommended.

**Q: Network needed for AI reports?**
A: Yes, for API calls to OpenAI/Claude.

### Support

**Q: Where to report bugs?**
A: GitHub Issues page or email support.

**Q: Is there video training?**
A: Video tutorials in development.

**Q: Commercial support?**
A: Contact author for professional services.

---

## Appendices

### Keyboard Shortcuts
- **Esc**: Cancel drawing
- **Delete**: Clear profiles
- **F1**: Open help

### File Locations
- **Settings**: `~/.qgis3/profiles/default/`
- **Logs**: `~/.qgis3/profiles/default/python/plugins/dual_profile_viewer/logs/`
- **Cache**: System temp directory

### Updates
Check for updates in QGIS Plugin Manager or GitHub releases page.

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Author**: Enzo Cocca  
**License**: GPL v3.0