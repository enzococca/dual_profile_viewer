# 3D Geological Viewers Comparison

## PyVista Geological Viewer vs Plotly Geological Viewer

### PyVista Geological Viewer
**Technology**: Uses PyVista (VTK-based) for 3D rendering in a Qt widget

**Features**:
- Real-time interactive 3D visualization within QGIS
- 3D wall representations of geological sections
- Click-to-select sections for attribute viewing
- Stratigraphic layer visualization with color bands
- Wall intersection calculations and highlighting
- Reference plane for elevation comparison
- Export to 3D formats (STL, OBJ, VTK)
- Screenshot export functionality
- "Show All Sections" checkbox to view multiple sections simultaneously

**Advantages**:
- Integrated directly into QGIS interface
- Better performance for complex 3D meshes
- More advanced 3D interaction (rotation, zoom, pan)
- Can handle larger datasets efficiently
- Direct mesh manipulation capabilities

**Requirements**:
- Requires PyVista and PyVistaQt packages
- More demanding on system resources

### Plotly Geological Viewer
**Technology**: Uses Plotly for 3D visualization in web browser

**Features**:
- Web-based interactive 3D visualization
- 3D wall representations with transparency
- Geological layer visualization
- Intersection highlighting
- Export to HTML for sharing
- Works with section layers from QGIS project

**Advantages**:
- No additional Qt dependencies needed
- Easy to share visualizations (HTML export)
- Works in any web browser
- Better for creating reports and presentations
- More customizable styling options

**Requirements**:
- Requires Plotly package
- Opens in external web browser

## When to Use Each

### Use PyVista Geological Viewer when:
- You need to work within QGIS interface
- You have complex 3D data to visualize
- You need to export 3D models for other software
- You want real-time interaction with your data
- You need to analyze wall intersections

### Use Plotly Geological Viewer when:
- You need to share visualizations with others
- You want to create web-based reports
- You prefer browser-based interaction
- You need highly customizable plots
- You want to embed visualizations in presentations

## Key Differences

1. **Rendering Location**:
   - PyVista: Renders inside QGIS window
   - Plotly: Renders in web browser

2. **Performance**:
   - PyVista: Better for large datasets
   - Plotly: Better for smaller, presentation-ready visualizations

3. **Export Options**:
   - PyVista: 3D model formats (STL, OBJ, VTK) + images
   - Plotly: HTML + images

4. **Interaction**:
   - PyVista: Professional 3D CAD-like controls
   - Plotly: Web-based intuitive controls

5. **Dependencies**:
   - PyVista: Heavier (requires VTK backend)
   - Plotly: Lighter (just needs web browser)

## Summary
Both viewers serve different purposes. PyVista is better for technical analysis and working within QGIS, while Plotly is better for creating shareable visualizations and reports. The choice depends on your specific workflow and requirements.