# Stratigraph Integration for Dual Profile Viewer

This document describes the integration of the stratigraph library into the Dual Profile Viewer QGIS plugin.

## Features

### 1. Module Installation System
- **Automatic dependency checking**: The plugin checks for required Python modules on startup
- **Background installation**: Missing modules can be installed in the background without blocking QGIS
- **Progress tracking**: Real-time feedback during module installation
- **Required modules**:
  - matplotlib
  - numpy
  - mayavi (for 3D visualization)
  - scipy
  - scikit-learn
  - scikit-image
  - Pillow
  - shapely
  - tqdm
  - stratigraph

### 2. 3D Stratigraphic Visualization
- **3D profile visualization**: Convert 2D elevation profiles into 3D stratigraphic models
- **Layer visualization**: Display stratigraphic layers with customizable boundaries
- **Exploded view**: Separate layers vertically for better visualization
- **Customizable appearance**: Choose colormaps, grid display, and other visual settings
- **Cross-section generation**: Extend profiles into 3D cross-sections

### 3. Stratigraphic Analysis Features
- **Automatic layer detection**: Analyze elevation profiles to detect stratigraphic layers
- **Deposition rate calculation**: Calculate theoretical deposition rates for each layer
- **Synthetic borehole generation**: Create virtual boreholes from profile data
- **Wheeler diagram generation**: Create chronostratigraphic diagrams
- **Barrell plot generation**: Generate time-elevation plots

### 4. Data Export
- **3D model export**: Export data formatted for 3D stratigraphic modeling software
- **Stratigraph format**: Export in formats compatible with the stratigraph library
- **JSON export**: Structured data export for further analysis

## Usage

### Installing Dependencies

1. Open the Dual Profile Viewer plugin
2. Click on "3D Stratigraphic Visualization" button
3. If modules are missing, click "Install Missing Modules"
4. Wait for installation to complete
5. Restart QGIS to use the new features

### Creating 3D Visualizations

1. Create elevation profiles using the main Dual Profile Viewer tool
2. Click "3D Stratigraphic Visualization"
3. Configure visualization settings:
   - Number of layers
   - Cross-section width
   - Display options (layers, grid, exploded view)
   - Colormap selection
4. Click "Create 3D Visualization"

### Stratigraphic Analysis

The plugin automatically analyzes profiles to:
- Detect layer boundaries based on elevation changes
- Calculate layer thickness and slope
- Generate synthetic stratigraphic data

## Technical Implementation

### Module Structure

- `module_installer.py`: Handles dependency checking and installation
- `stratigraph_integration.py`: Core integration with stratigraph library
- `stratigraph_3d_dialog.py`: UI for 3D visualization settings
- `stratigraph_features.py`: Advanced stratigraphic analysis features

### Key Classes

1. **ModuleInstaller**
   - Checks for missing Python modules
   - Installs modules using pip in a separate thread
   - Provides progress updates via Qt signals

2. **StratigraphIntegration**
   - Loads profile data from the main plugin
   - Creates stratigraphic models
   - Generates 3D visualizations using Mayavi
   - Exports data in various formats

3. **Stratigraph3DDialog**
   - User interface for 3D visualization settings
   - Module status display
   - Visualization parameter controls

4. **StratigraphFeatures**
   - Advanced stratigraphic analysis
   - Layer detection algorithms
   - Synthetic data generation

## Troubleshooting

### Mayavi Installation Issues

Mayavi requires VTK and can be challenging to install. If you encounter issues:

1. **Windows**: Install Visual C++ redistributables
2. **macOS**: Ensure Xcode command line tools are installed
3. **Linux**: Install system packages: `python3-vtk`, `python3-mayavi`

### Alternative Installation

If automatic installation fails:

```bash
# In QGIS Python console or system terminal
pip install matplotlib numpy scipy scikit-learn scikit-image Pillow shapely tqdm
pip install mayavi
pip install stratigraph
```

### 3D Visualization Not Working

If 3D visualization fails:
1. Check that Mayavi is properly installed
2. Ensure you have a display environment (X11 on Linux)
3. Try running a simple Mayavi test in QGIS Python console

## Future Enhancements

- Integration with more stratigraph features
- Support for time-series stratigraphic data
- Advanced layer correlation algorithms
- Integration with geological databases
- Support for borehole data import
- Enhanced 3D visualization options