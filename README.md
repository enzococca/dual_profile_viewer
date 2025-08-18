# Dual Profile Viewer

A QGIS plugin for archaeological dual profile analysis with georeferenced vector export capabilities.

![QGIS Version](https://img.shields.io/badge/QGIS-3.0+-green.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)

## Overview

The Dual Profile Viewer plugin creates parallel elevation profiles from DEM/DTM data, specifically designed for archaeological analysis. This tool is perfect for analyzing walls, structures, excavations, and terrain features by providing dual parallel profiles with adjustable offset.

## Features

- **Dual Parallel Profiles**: Create two parallel elevation profiles with adjustable offset distance
- **Interactive Visualization**: Dynamic Plotly graphs with zoom, pan, and hover capabilities
- **Multi-DEM Comparison**: Compare elevation data from multiple DEM/DTM layers
- **Georeferenced Export**: Export profiles as georeferenced vectors (polylines/polygons)
- **Multiple Export Formats**:
  - Vector layers (Shapefile, GeoPackage, etc.)
  - CSV data export
  - PNG images with world files
  - Interactive HTML graphs
- **Real-time Preview**: See profile lines on the map as you draw
- **Automatic Labeling**: Section labels for easy identification
- **3D Export**: Export profiles with real elevation values

## Installation

### From QGIS Plugin Repository (Recommended)
1. Open QGIS
2. Go to `Plugins` → `Manage and Install Plugins`
3. Search for "Dual Profile Viewer"
4. Click `Install Plugin`

### Manual Installation
1. Download the plugin zip file
2. In QGIS, go to `Plugins` → `Manage and Install Plugins`
3. Select `Install from ZIP`
4. Choose the downloaded file
5. Click `Install Plugin`

### Development Installation
```bash
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
git clone https://github.com/enzococca/dual-profile-viewer.git
```

## Usage

### Basic Workflow

1. **Load DEM/DTM Data**: 
   - Add your elevation raster layers to the QGIS project
   - Supported formats: GeoTIFF, ASCII Grid, etc.

2. **Open the Plugin**:
   - Click the Dual Profile Viewer icon in the toolbar
   - Or go to `Raster` → `Dual Profile Viewer`

3. **Select Raster Layer**:
   - Choose your DEM/DTM from the dropdown
   - Enable multi-DEM comparison if needed

4. **Set Profile Parameters**:
   - Adjust the offset distance (distance between parallel profiles)
   - Set sampling interval if needed

5. **Draw Profile Line**:
   - Click `Draw Profile` button
   - Click on the map to set the start point
   - Click again to set the end point
   - The dual profiles will be automatically generated

6. **Analyze Results**:
   - View elevation profiles in the interactive graph
   - Check statistics (min, max, mean elevation)
   - Compare profiles side by side

7. **Export Options**:
   - **Vector Export**: Save as georeferenced polylines or polygons
   - **CSV Export**: Export elevation data for further analysis
   - **Image Export**: Save as PNG with georeferencing

### Advanced Features

#### Multi-DEM Comparison
1. Check "Enable multi-DEM comparison"
2. Select additional DEM layers
3. Profiles will show elevation from all selected layers

#### Vector Export Options
- **Polyline**: Exports the profile curve as a line feature
- **Polygon**: Creates a filled polygon from baseline to profile
- **3D Polyline**: Includes real elevation values in geometry

#### Scaling Options
- **Vertical Exaggeration**: Enhance elevation differences
- **Overall Scale**: Scale the entire profile
- **Baseline Offset**: Adjust the vertical position

## Requirements

- QGIS 3.0 or higher
- Python packages (automatically installed):
  - numpy
  - plotly (optional, falls back to matplotlib)

## Troubleshooting

### Common Issues

1. **No profile displayed**:
   - Ensure DEM layer is properly loaded
   - Check that the profile line intersects the raster extent
   - Verify the raster has valid elevation values

2. **Export fails**:
   - Check write permissions for output directory
   - Ensure valid output format is selected
   - Verify CRS compatibility

3. **Plotly graphs not showing**:
   - Install plotly: `pip install plotly`
   - Plugin will fall back to matplotlib if unavailable

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Author

**Enzo Cocca**
- Email: enzo.ccc@gmail.com
- GitHub: [@enzococca](https://github.com/enzococca)

## Acknowledgments

- QGIS Development Team for the excellent plugin framework
- Archaeological community for feedback and testing
- Contributors and testers

## Citation

If you use this plugin in your research, please cite:
```
Cocca, E. (2025). Dual Profile Viewer: A QGIS Plugin for Archaeological Profile Analysis. 
Available at: https://github.com/enzococca/dual-profile-viewer
```

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/enzococca/dual-profile-viewer/issues)
- **Documentation**: [Wiki](https://github.com/enzococca/dual-profile-viewer/wiki)
- **Email**: enzo.ccc@gmail.com

## Changelog

### Version 1.0.0 (2025-08-18)
- Initial release
- Dual profile extraction from DEM/DTM
- Interactive Plotly visualization
- Export as georeferenced vector (polyline/polygon)
- Multi-DEM comparison
- CSV and vector export with georeferencing