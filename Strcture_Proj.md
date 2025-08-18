# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a QGIS plugin called "Dual Profile Viewer" - an archaeological dual profile analysis tool with georeferenced vector export capabilities. The plugin creates parallel elevation profiles from DEM/DTM data for archaeological analysis.

## Architecture

The plugin follows the standard QGIS Python plugin structure:

1. **Entry Point**: `__init__.py` - Contains `classFactory()` that instantiates the main plugin class
2. **Main Plugin Class**: `dual_profile_viewer.py` - Implements `DualProfileViewer` class that handles QGIS integration, toolbar creation, and plugin lifecycle
3. **Core Functionality**: `dual_profile_tool.py` - Contains:
   - `DualProfileTool` - QgsMapTool for drawing profile lines on the map
   - `ProfileViewerDialog` - Main dialog window for profile visualization and analysis
4. **Export Functionality**: 
   - `profile_exporter.py` - Handles exporting profiles as georeferenced vectors (polylines/polygons/3D)
   - `vector_export_dialog.py` - UI dialog for vector export options
5. **Plugin Metadata**: `metadata.txt` - Contains plugin information, version, and description

## Key Dependencies

- QGIS PyQt API (qgis.core, qgis.gui, qgis.PyQt)
- NumPy for profile calculations
- Plotly (optional) for interactive graphs - falls back to matplotlib if not available
- Standard Python libraries: math, datetime, os, tempfile, webbrowser

## Development Commands

This is a QGIS plugin, so there are no traditional build/test commands. Development workflow:

1. **Plugin Location**: Place in QGIS plugins directory at `[QGIS Profile]/python/plugins/dual_profile_viewer`
2. **Reload Plugin**: Use the Plugin Reloader plugin in QGIS to reload after changes
3. **Debug**: Use QGIS Python Console for debugging and testing
4. **Resource Compilation**: If modifying `resources.qrc`, compile with: `pyrcc5 -o resources.py resources.qrc`

## Plugin Features

- Dual parallel profile extraction from DEM/DTM raster layers
- Interactive profile drawing with adjustable offset distance
- Multi-DEM comparison capabilities
- Export options:
  - Georeferenced vector layers (polyline/polygon/3D)
  - CSV data export
  - PNG with world files
  - Plotly interactive HTML graphs
- Real-time profile visualization with elevation statistics