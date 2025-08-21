# Dual Profile Viewer - QGIS Plugin

🏛️ **Advanced Elevation Profile Analysis Tool for QGIS**

[![QGIS Version](https://img.shields.io/badge/QGIS-3.16+-green.svg)](https://qgis.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org)

## 🎯 Overview

The **Dual Profile Viewer** is a comprehensive QGIS plugin for advanced elevation profile analysis featuring single/dual profile modes, multi-section polygon support, 3D visualization, and AI-powered reporting. Designed for archaeologists, geologists, engineers, and GIS professionals.

## 🌟 Key Features

### Core Functionality
- **Single Profile Mode**: Draw individual elevation profiles
- **Dual Profile Mode**: Create parallel profiles with adjustable offset
- **Polygon Multi-Section**: Automatically generate profiles for each polygon side
- **Multi-DEM Comparison**: Compare profiles across multiple elevation models

### Advanced Visualization
- **2D Interactive Plots**: Matplotlib and Plotly integration
- **3D Terrain Viewer**: PyVista-based advanced 3D visualization
- **Web 3D Viewer**: Plotly-based browser visualization
- **Real-time Preview**: See profiles while drawing

### Professional Output
- **Layout Generation**: Automated PDF/image layouts
- **Vector Export**: GeoPackage, Shapefile, 3D vectors
- **AI Reports**: GPT-4/Claude integration for analysis
- **Statistics**: Comprehensive elevation metrics

## 📋 Requirements

- QGIS 3.16 or higher
- Python 3.7+
- Core dependencies (auto-installed):
  - numpy
  - matplotlib
  - plotly
- Optional dependencies:
  - pyvista (3D visualization)
  - vtk (required by pyvista)
  - requests (AI reports)

## 🚀 Installation

### From QGIS Plugin Repository
1. Open QGIS
2. Go to `Plugins` → `Manage and Install Plugins`
3. Search for "Dual Profile Viewer"
4. Click `Install Plugin`

### Manual Installation
```bash
# Download or clone the repository
git clone https://github.com/yourusername/dual_profile_viewer.git

# Copy to QGIS plugins folder
# Windows
copy dual_profile_viewer %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\

# macOS
cp -r dual_profile_viewer ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/

# Linux
cp -r dual_profile_viewer ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

### Installing Optional Dependencies
```bash
# For 3D visualization
pip install pyvista vtk

# For AI reports
pip install requests
```

## 📖 Step-by-Step Usage Guide

### 1. Getting Started

#### Opening the Plugin
1. Load your DEM/DTM raster layer in QGIS
2. Click the Dual Profile Viewer icon in the toolbar
3. Or go to `Plugins` → `Dual Profile Viewer`

#### Interface Overview
- **DEM Selection**: Choose your elevation model
- **Drawing Tools**: Single, Dual, or Polygon section buttons
- **Parameters**: Offset distance, sample points
- **Visualization**: 2D plots, 3D viewers
- **Export Options**: Vector, layout, statistics

### 2. Drawing Profiles

#### Single Section Mode
1. Click `Single Section` button
2. Click on map to set start point
3. Move mouse (see real-time preview)
4. Click to set end point
5. Profile appears in plot area

#### Dual Section Mode (Default)
1. Click `Draw Section` button
2. Set offset distance (meters)
3. Draw main profile line (A-A')
4. Parallel profile (B-B') created automatically
5. Both profiles shown in plot

#### Polygon Multi-Section Mode
1. Click `Polygon Section` button
2. Click to create polygon vertices
3. Right-click to complete polygon
4. One profile generated per side
5. All sections displayed together

### 3. Adjusting Parameters

#### Offset Distance (Dual Mode)
- **Range**: 0.5 - 1000 meters
- **Default**: 10 meters
- **Usage**: Distance between parallel profiles
- **Real-time**: Updates during drawing

#### Sample Points
- **Range**: 50 - 1000 points
- **Default**: 200 points
- **Higher**: More detail, slower processing
- **Lower**: Faster, less detail

### 4. Visualization Options

#### 2D Profile Plots

**Matplotlib (Static)**
- Traditional elevation plot
- Print-ready quality
- Basic interaction

**Plotly (Interactive)**
- Zoom, pan, hover details
- Export to HTML
- Advanced tooltips

#### 3D Visualization

**PyVista 3D Viewer**
- Full 3D terrain model
- Section lines highlighted
- Intersection visualization
- Controls:
  - Left mouse: Rotate
  - Right mouse: Zoom
  - Middle mouse: Pan
  - 'r': Reset view
  - 'w': Wireframe
  - 's': Surface

**Plotly Web 3D**
- Browser-based viewer
- No additional dependencies
- Share via HTML

### 5. Multi-DEM Analysis

1. **Add DEMs**: Click `Browse` button
2. **Select Files**: Choose multiple DEMs
3. **View List**: Selected DEMs appear in widget
4. **Compare**: Profiles extracted from all DEMs
5. **Visualize**: Side-by-side comparison

### 6. Data Export

#### Vector Export Options

**Profile as Polyline**
- Elevation profile as 3D line
- Maintains elevation values
- GeoPackage or Shapefile

**Profile as Polygon**
- Filled area under profile
- Useful for volume calculations
- Includes baseline

**3D Vector**
- True 3D coordinates
- Compatible with 3D GIS
- Z-values preserved

#### Export Steps
1. Click `Export` button
2. Choose export type
3. Set parameters:
   - Vertical exaggeration
   - Scale factor
   - Baseline offset
4. Select output file
5. Optionally add to map

### 7. Layout Generation

#### Single Section Layout
- One page document
- Contains:
  - Location map (right)
  - Profile plot (left)
  - Statistics table
  - Scale bar
  - Title and labels

#### Multi-Section Layout
- One page per section
- Each page includes:
  - Section-specific map
  - Individual profile
  - Section statistics
  - Consistent formatting
- Optional AI report as final page

#### Creating Layouts
1. Click `Layout` button
2. Configure options:
   - Page size (A4, A3, etc.)
   - Orientation
   - Map scale
3. Generate layout
4. Export to PDF/Image

### 8. Statistics and Analysis

#### Available Metrics
- **Elevation**: Min, Max, Mean, Range
- **Slope**: Average, Maximum
- **Distance**: Total length, Sampling interval
- **Profile**: Curvature, Roughness

#### Viewing Statistics
1. Click `Statistics` button
2. View in text window
3. Copy to clipboard
4. Export to file

### 9. AI Report Generation

#### Setup (First Time)
1. Click `AI Report` button
2. Select AI service:
   - OpenAI GPT-4
   - Anthropic Claude
3. Enter API key
4. Key saved for future use

#### Generating Reports
1. Select report options:
   - Statistical analysis
   - Geological interpretation
   - Recommendations
2. Choose technical level:
   - Basic
   - Intermediate
   - Advanced
3. Click `Generate Report`
4. Review and export

## 🛠️ Advanced Features

### Custom Symbology
- Single sections: Simple red line
- Dual sections: Red (A-A') and Blue (B-B')
- Polygon sections: Color-coded by side

### Batch Processing
```python
# Process multiple sections
for feature in layer.getFeatures():
    # Extract profile for each feature
    profile = viewer.extract_profile(feature.geometry())
```

### Integration with QGIS
- Attribute table integration
- Processing toolbox compatibility
- Python console access

## 🐛 Troubleshooting

### Common Issues and Solutions

#### PyVista 3D Viewer Won't Open
```bash
# Install with conda (recommended)
conda install -c conda-forge pyvista

# Or with pip
pip install pyvista vtk
```

#### No Elevation Data in Profile
- Check DEM covers profile area
- Verify CRS compatibility
- Look for no-data values
- Ensure DEM is loaded correctly

#### Export Creates Empty File
- Verify elevation data exists
- Check file permissions
- Try different format
- Ensure sufficient disk space

#### Matplotlib Plot Not Showing
- Check backend settings
- Update matplotlib: `pip install -U matplotlib`
- Restart QGIS

### Performance Optimization
- Reduce sample points for large areas
- Use Plotly instead of PyVista for many sections
- Close unused viewers
- Clear old profiles before new analysis

## 📊 Use Cases

### Archaeological Applications
- Ancient fortifications
- Settlement analysis
- Road and path systems
- Landscape archaeology

### Geological Studies
- Fault analysis
- Stratigraphic sections
- Volcanic profiles
- Sedimentary basins

### Engineering Projects
- Road design
- Pipeline planning
- Railway profiles
- Slope stability

### Environmental Analysis
- River profiles
- Watershed studies
- Erosion assessment
- Habitat analysis

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push branch (`git push origin feature/NewFeature`)
5. Open Pull Request

## 📄 License

GNU General Public License v3.0 - see [LICENSE](LICENSE) file

## 👥 Credits

**Author**: Enzo Cocca
**Email**: enzo.ccc@gmail.com
**Contributors**: See [CONTRIBUTORS.md](CONTRIBUTORS.md)

## 🙏 Acknowledgments

- QGIS Development Team
- PyVista Community
- Plotly Technologies
- All users and testers

## 📚 Additional Resources

- [User Manual](USER_MANUAL.md) - Detailed documentation
- [GitHub Issues](https://github.com/yourusername/dual_profile_viewer/issues) - Bug reports
- [Wiki](https://github.com/yourusername/dual_profile_viewer/wiki) - Additional guides

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**QGIS Minimum Version**: 3.16  
**Python**: 3.7+