# -*- coding: utf-8 -*-
"""
Dual Profile Tool - Main dialog and drawing tool
Adapted from the original script for plugin structure
"""

from qgis.PyQt import QtWidgets, QtCore
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import Qt, QVariant

from qgis.core import (
    # Basics
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPoint, QgsPointXY, QgsLineString, QgsWkbTypes,
    QgsField, QgsFields, QgsVectorFileWriter,
    QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    
    # Raster
    QgsRasterLayer, QgsRaster,
    
    # Symbology
    QgsSymbol, QgsSimpleLineSymbolLayer,
    QgsSingleSymbolRenderer, QgsMarkerSymbol,
    QgsSimpleMarkerSymbolLayer,
    QgsCategorizedSymbolRenderer, QgsRendererCategory,
    
    # Labeling
    QgsTextFormat, QgsVectorLayerSimpleLabeling,
    QgsPalLayerSettings, QgsTextBufferSettings,
    
    # General
    Qgis
)
from qgis.gui import QgsMapTool, QgsRubberBand, QgsMapToolEmitPoint
import math
import numpy as np
from datetime import datetime
import os
import tempfile
import webbrowser

# Import profile exporter
from .profile_exporter import ProfileExporter
from .vector_export_dialog import VectorExportDialog

# Try to import plotly
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("⚠️ plotly not available. Install with: pip install plotly")

# Fallback to matplotlib
if not PLOTLY_AVAILABLE:
    try:
        import matplotlib
        matplotlib.use('Qt5Agg')
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        import matplotlib.pyplot as plt
        MATPLOTLIB_AVAILABLE = True
    except ImportError:
        MATPLOTLIB_AVAILABLE = False

class DualProfileTool(QgsMapTool):
    """Tool for drawing two parallel lines centered on the drawn line"""
    
    def __init__(self, canvas, callback):
        super().__init__(canvas)
        self.canvas = canvas
        self.callback = callback
        self.rubber_band_center = None
        self.rubber_band1 = None
        self.rubber_band2 = None
        self.start_point = None
        self.end_point = None
        self.is_drawing = False
        self.offset_distance = 1.0
        
    def canvasPressEvent(self, event):
        """Handle mouse clicks"""
        if event.button() == Qt.LeftButton:
            point = self.toMapCoordinates(event.pos())
            
            if not self.is_drawing:
                # First click: start drawing
                self.start_point = point
                self.is_drawing = True
                
                # Create rubber bands
                self.rubber_band_center = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
                self.rubber_band_center.setColor(QColor(128, 128, 128, 30))
                self.rubber_band_center.setWidth(0.5)
                self.rubber_band_center.setLineStyle(Qt.DashLine)
                
                self.rubber_band1 = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
                self.rubber_band1.setColor(QColor(255, 0, 0, 200))
                self.rubber_band1.setWidth(2)
                
                self.rubber_band2 = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
                self.rubber_band2.setColor(QColor(0, 0, 255, 200))
                self.rubber_band2.setWidth(2)
            else:
                # Second click: complete drawing
                self.end_point = point
                self.finalize_drawing()
                
    def canvasMoveEvent(self, event):
        """Update visualization while moving mouse"""
        if self.is_drawing and self.start_point:
            current_point = self.toMapCoordinates(event.pos())
            
            # Calculate parallel lines
            line1, line2 = self.calculate_parallel_lines(
                self.start_point, current_point, self.offset_distance
            )
            
            # Update rubber bands
            if self.rubber_band_center:
                self.rubber_band_center.reset(QgsWkbTypes.LineGeometry)
                self.rubber_band_center.addPoint(self.start_point)
                self.rubber_band_center.addPoint(current_point)
            
            if self.rubber_band1:
                self.rubber_band1.reset(QgsWkbTypes.LineGeometry)
                for point in line1:
                    self.rubber_band1.addPoint(point)
                    
            if self.rubber_band2:
                self.rubber_band2.reset(QgsWkbTypes.LineGeometry)
                for point in line2:
                    self.rubber_band2.addPoint(point)
                    
    def calculate_parallel_lines(self, start, end, offset):
        """Calculate two parallel lines equidistant from the center line"""
        # Calculate line angle
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        angle = math.atan2(dy, dx)
        
        # Perpendicular angle
        perp_angle = angle + math.pi / 2
        
        # Calculate offset
        offset_x = offset * math.cos(perp_angle)
        offset_y = offset * math.sin(perp_angle)
        
        # Line 1 (A-A' - upper/left)
        line1_start = QgsPointXY(start.x() + offset_x, start.y() + offset_y)
        line1_end = QgsPointXY(end.x() + offset_x, end.y() + offset_y)
        
        # Line 2 (B-B' - lower/right)
        line2_start = QgsPointXY(start.x() - offset_x, start.y() - offset_y)
        line2_end = QgsPointXY(end.x() - offset_x, end.y() - offset_y)
        
        return [line1_start, line1_end], [line2_start, line2_end]
    
    def finalize_drawing(self):
        """Complete drawing and call callback"""
        if self.start_point and self.end_point:
            # Calculate final lines
            line1, line2 = self.calculate_parallel_lines(
                self.start_point, self.end_point, self.offset_distance
            )
            
            # Pass lines to callback
            self.callback(line1, line2, [self.start_point, self.end_point])
            
        # Clean up
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources"""
        for rubber_band in [self.rubber_band_center, self.rubber_band1, self.rubber_band2]:
            if rubber_band:
                self.canvas.scene().removeItem(rubber_band)
        self.rubber_band_center = None
        self.rubber_band1 = None
        self.rubber_band2 = None
        self.start_point = None
        self.end_point = None
        self.is_drawing = False
        
    def deactivate(self):
        """Called when tool is deactivated"""
        self.cleanup()
        super().deactivate()
        
    def keyPressEvent(self, event):
        """Handle ESC to cancel"""
        if event.key() == Qt.Key_Escape:
            self.cleanup()

class ProfileViewerDialog(QtWidgets.QDialog):
    """Main dialog for displaying profiles"""
    
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("Dual Profile Viewer - Archaeological Analysis")
        self.setMinimumSize(1000, 700)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the interface"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()
        
        # DEM selection
        toolbar.addWidget(QtWidgets.QLabel("Primary DEM:"))
        self.combo_dem = QtWidgets.QComboBox()
        self.load_raster_layers(self.combo_dem)
        toolbar.addWidget(self.combo_dem)
        
        # Secondary DEM
        self.check_multi_dem = QtWidgets.QCheckBox("Compare DEMs")
        self.check_multi_dem.toggled.connect(self.on_multi_dem_toggled)
        toolbar.addWidget(self.check_multi_dem)
        
        self.combo_dem2 = QtWidgets.QComboBox()
        self.combo_dem2.setVisible(False)
        self.load_raster_layers(self.combo_dem2)
        toolbar.addWidget(self.combo_dem2)
        
        # Offset distance
        toolbar.addWidget(QtWidgets.QLabel("Offset:"))
        self.spin_distance = QtWidgets.QDoubleSpinBox()
        self.spin_distance.setMinimum(0.05)
        self.spin_distance.setMaximum(500.0)
        self.spin_distance.setValue(1.0)
        self.spin_distance.setSingleStep(0.05)
        self.spin_distance.setDecimals(2)
        self.spin_distance.setSuffix(" m")
        toolbar.addWidget(self.spin_distance)
        
        # Samples
        toolbar.addWidget(QtWidgets.QLabel("Samples:"))
        self.spin_samples = QtWidgets.QSpinBox()
        self.spin_samples.setMinimum(10)
        self.spin_samples.setMaximum(2000)
        self.spin_samples.setValue(200)
        toolbar.addWidget(self.spin_samples)
        
        toolbar.addStretch()
        
        # Action buttons
        self.btn_draw = QtWidgets.QPushButton("🎯 Draw Sections")
        self.btn_draw.clicked.connect(self.start_drawing)
        toolbar.addWidget(self.btn_draw)
        
        self.btn_create_layer = QtWidgets.QPushButton("📍 Create Section Layer")
        self.btn_create_layer.clicked.connect(self.create_section_layer)
        self.btn_create_layer.setEnabled(False)
        toolbar.addWidget(self.btn_create_layer)
        
        self.btn_export_vector = QtWidgets.QPushButton("📐 Export Vector Profile")
        self.btn_export_vector.clicked.connect(self.export_vector_profile)
        self.btn_export_vector.setEnabled(False)
        toolbar.addWidget(self.btn_export_vector)
        
        self.btn_export_data = QtWidgets.QPushButton("💾 Export CSV")
        self.btn_export_data.clicked.connect(self.export_data)
        self.btn_export_data.setEnabled(False)
        toolbar.addWidget(self.btn_export_data)
        
        toolbar.addWidget(QtWidgets.QWidget())  # Spacer
        
        self.btn_help = QtWidgets.QPushButton("❓ Help")
        self.btn_help.clicked.connect(self.show_help)
        self.btn_help.setToolTip("Open user manual")
        toolbar.addWidget(self.btn_help)
        
        layout.addLayout(toolbar)
        
        # Graph area
        info_label = QtWidgets.QLabel(
            "📊 Dual Profile Viewer for Archaeological Analysis\n\n"
            "✅ Graphs will open automatically in your browser\n"
            "✅ Export profiles as georeferenced vectors\n"
            "✅ Multi-DEM comparison support\n\n"
            "Click 'Draw Sections' to begin analysis"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setMinimumHeight(400)
        info_label.setStyleSheet("""
            QLabel { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f4f8, stop:1 #d9e2ec);
                border: 2px solid #627d98;
                border-radius: 8px;
                font-size: 14px;
                padding: 20px;
                color: #102a43;
            }
        """)
        layout.addWidget(info_label)
        
        # Info text area
        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        
        # Variables
        self.profile_data = None
        self.profile_data_list = []  # For 3D viewer
        self.map_tool = None
        self.section_count = 0
        self.current_figure = None
        
    def load_raster_layers(self, combo=None):
        """Load available raster layers"""
        if combo is None:
            combo = self.combo_dem
            
        combo.clear()
        
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsRasterLayer) and layer.bandCount() > 0:
                combo.addItem(layer.name(), layer.id())
                
        if combo.count() == 0:
            combo.addItem("(No DEM/DTM found)", None)
            
    def on_multi_dem_toggled(self, checked):
        """Toggle visibility of second DEM selector"""
        self.combo_dem2.setVisible(checked)
        if checked:
            self.load_raster_layers(self.combo_dem2)
            
    def start_drawing(self):
        """Activate drawing tool"""
        if self.combo_dem.currentData() is None:
            QtWidgets.QMessageBox.warning(
                self, 
                "Warning", 
                "Please select a DEM/DTM layer first!"
            )
            return
            
        # Set distance in tool
        canvas = self.iface.mapCanvas()
        
        # Deactivate previous tool if exists
        if self.map_tool:
            canvas.unsetMapTool(self.map_tool)
            
        # Create new tool
        self.map_tool = DualProfileTool(canvas, self.on_lines_drawn)
        self.map_tool.offset_distance = self.spin_distance.value()
        
        # Activate tool
        canvas.setMapTool(self.map_tool)
        
        self.info_text.setText("Click two points on the map to draw parallel sections...\n"
                              "The sections will be created parallel to and equidistant from your drawn line.")
        
    def on_lines_drawn(self, line1, line2, center_line):
        """Called when lines have been drawn"""
        # Deactivate tool
        self.iface.mapCanvas().unsetMapTool(self.map_tool)
        
        # Extract profiles
        self.extract_profiles(line1, line2, center_line)
        
    def extract_profiles(self, line1, line2, center_line):
        """Extract elevation profiles from lines"""
        dem_layer_id = self.combo_dem.currentData()
        if not dem_layer_id:
            return
            
        dem_layer = QgsProject.instance().mapLayer(dem_layer_id)
        if not dem_layer:
            return
            
        num_samples = self.spin_samples.value()
        
        # Extract profiles
        profile1 = self.sample_raster_along_line(
            dem_layer, line1[0], line1[1], num_samples
        )
        
        profile2 = self.sample_raster_along_line(
            dem_layer, line2[0], line2[1], num_samples
        )
        
        # Debug primary DEM
        valid_count1 = np.sum(~np.isnan(profile1['elevations']))
        print(f"DEM1 ({dem_layer.name()}): {valid_count1}/{num_samples} valid points")
        
        # Check for second DEM
        profile1_dem2 = None
        profile2_dem2 = None
        dem2_name = None
        
        if self.check_multi_dem.isChecked():
            dem2_layer_id = self.combo_dem2.currentData()
            if dem2_layer_id:
                dem2_layer = QgsProject.instance().mapLayer(dem2_layer_id)
                if dem2_layer:
                    dem2_name = dem2_layer.name()
                    
                    # Check if DEMs have same CRS
                    if dem_layer.crs() != dem2_layer.crs():
                        QtWidgets.QMessageBox.warning(
                            self,
                            "CRS Mismatch",
                            f"Warning: DEMs have different coordinate systems!\n"
                            f"DEM1: {dem_layer.crs().authid()}\n"
                            f"DEM2: {dem2_layer.crs().authid()}\n\n"
                            f"Results may be incorrect. Consider reprojecting one DEM."
                        )
                    
                    profile1_dem2 = self.sample_raster_along_line(
                        dem2_layer, line1[0], line1[1], num_samples
                    )
                    profile2_dem2 = self.sample_raster_along_line(
                        dem2_layer, line2[0], line2[1], num_samples
                    )
                    
                    # Debug secondary DEM
                    valid_count2_a = np.sum(~np.isnan(profile1_dem2['elevations']))
                    valid_count2_b = np.sum(~np.isnan(profile2_dem2['elevations']))
                    print(f"DEM2 ({dem2_name}): A-A' {valid_count2_a}/{num_samples}, B-B' {valid_count2_b}/{num_samples} valid points")
                    
                    if valid_count2_a == 0 and valid_count2_b == 0:
                        QtWidgets.QMessageBox.warning(
                            self,
                            "No Data in Second DEM",
                            f"The second DEM '{dem2_name}' has no valid elevation data\n"
                            f"in the selected area.\n\n"
                            f"Check that:\n"
                            f"1. The DEM covers this area\n"
                            f"2. The DEM has valid elevation values\n"
                            f"3. Both DEMs use the same coordinate system"
                        )
                        # Reset to None to avoid plotting empty data
                        profile1_dem2 = None
                        profile2_dem2 = None
                        dem2_name = None
        
        # Save data
        self.profile_data = {
            'profile1': profile1,
            'profile2': profile2,
            'profile1_dem2': profile1_dem2,
            'profile2_dem2': profile2_dem2,
            'line1': line1,
            'line2': line2,
            'center_line': center_line,
            'offset': self.spin_distance.value(),
            'dem1_name': dem_layer.name(),
            'dem2_name': dem2_name
        }
        
        # Visualize
        self.plot_profiles(profile1, profile2, profile1_dem2, profile2_dem2)
        
        # Enable export buttons
        self.btn_export_data.setEnabled(True)
        self.btn_export_vector.setEnabled(True)
        self.btn_create_layer.setEnabled(True)
        
    def sample_raster_along_line(self, raster_layer, start_point, end_point, num_samples):
        """Sample raster along a line with better NoData handling"""
        # Create interpolated points along line
        x_coords = np.linspace(start_point.x(), end_point.x(), num_samples)
        y_coords = np.linspace(start_point.y(), end_point.y(), num_samples)
        
        # Calculate progressive distances
        distances = np.zeros(num_samples)
        elevations = np.zeros(num_samples)
        
        # Get NoData value for this raster
        provider = raster_layer.dataProvider()
        nodata_value = provider.sourceNoDataValue(1)  # Band 1
        
        # Check if points are within raster extent
        extent = raster_layer.extent()
        points_in_extent = 0
        
        for i in range(num_samples):
            if i > 0:
                dx = x_coords[i] - x_coords[i-1]
                dy = y_coords[i] - y_coords[i-1]
                distances[i] = distances[i-1] + math.sqrt(dx*dx + dy*dy)
            
            # Sample elevation
            sample_point = QgsPointXY(x_coords[i], y_coords[i])
            
            # Check if point is within raster extent
            if not extent.contains(sample_point):
                elevations[i] = np.nan
                continue
            
            points_in_extent += 1
            
            # Sample the raster value
            value, success = provider.sample(sample_point, 1)
            
            if success and value != nodata_value and not math.isnan(value):
                elevations[i] = value
            else:
                elevations[i] = np.nan
        
        # Debug output
        valid_count = np.sum(~np.isnan(elevations))
        if valid_count == 0:
            print(f"WARNING: No valid elevation data extracted from {raster_layer.name()}")
            print(f"  Points in extent: {points_in_extent}/{num_samples}")
            print(f"  NoData value: {nodata_value}")
            if points_in_extent > 0:
                print(f"  All values were NoData or failed to sample")
                
        return {
            'distances': distances,
            'elevations': elevations,
            'x_coords': x_coords,
            'y_coords': y_coords
        }
        
    def plot_profiles(self, profile1, profile2, profile1_dem2=None, profile2_dem2=None):
        """Display profiles with multi-DEM support"""
        has_multi_dem = profile1_dem2 is not None and profile2_dem2 is not None
        
        if PLOTLY_AVAILABLE:
            # Create Plotly figure
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=(
                    f'Parallel Profiles - Offset: {self.spin_distance.value():.2f}m',
                    "Elevation Difference (A-A' minus B-B')"
                ),
                vertical_spacing=0.15,
                row_heights=[0.6, 0.4]
            )
            
            # Add primary DEM profiles
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'], 
                    y=profile1['elevations'],
                    mode='lines',
                    name=f"A-A' ({self.profile_data['dem1_name']})",
                    line=dict(color='red', width=2),
                    hovertemplate='Distance: %{x:.2f}m<br>Elevation: %{y:.3f}m<extra></extra>'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=profile2['distances'], 
                    y=profile2['elevations'],
                    mode='lines',
                    name=f"B-B' ({self.profile_data['dem1_name']})",
                    line=dict(color='blue', width=2),
                    hovertemplate='Distance: %{x:.2f}m<br>Elevation: %{y:.3f}m<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Add fill between primary profiles
            fig.add_trace(
                go.Scatter(
                    x=np.concatenate([profile1['distances'], profile2['distances'][::-1]]),
                    y=np.concatenate([profile1['elevations'], profile2['elevations'][::-1]]),
                    fill='toself',
                    fillcolor='rgba(128, 128, 128, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Volume/Difference',
                    hoverinfo='skip',
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # Add secondary DEM profiles if available
            if has_multi_dem:
                fig.add_trace(
                    go.Scatter(
                        x=profile1_dem2['distances'], 
                        y=profile1_dem2['elevations'],
                        mode='lines',
                        name=f"A-A' ({self.profile_data['dem2_name']})",
                        line=dict(color='red', width=1.5, dash='dash'),
                        hovertemplate='Distance: %{x:.2f}m<br>Elevation: %{y:.3f}m<extra></extra>'
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=profile2_dem2['distances'], 
                        y=profile2_dem2['elevations'],
                        mode='lines',
                        name=f"B-B' ({self.profile_data['dem2_name']})",
                        line=dict(color='blue', width=1.5, dash='dash'),
                        hovertemplate='Distance: %{x:.2f}m<br>Elevation: %{y:.3f}m<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # Calculate and plot difference for primary DEM
            diff1 = profile1['elevations'] - profile2['elevations']
            
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'], 
                    y=diff1,
                    mode='lines',
                    name=f'Difference ({self.profile_data["dem1_name"]})',
                    line=dict(color='green', width=2),
                    hovertemplate='Distance: %{x:.2f}m<br>Difference: %{y:.3f}m<extra></extra>'
                ),
                row=2, col=1
            )
            
            # Add fills for positive/negative differences
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'],
                    y=np.where(diff1 >= 0, diff1, 0),
                    fill='tozeroy',
                    fillcolor='rgba(0, 255, 0, 0.3)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='A higher',
                    hoverinfo='skip',
                    showlegend=True
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'],
                    y=np.where(diff1 < 0, diff1, 0),
                    fill='tozeroy',
                    fillcolor='rgba(255, 0, 0, 0.3)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='B higher',
                    hoverinfo='skip',
                    showlegend=True
                ),
                row=2, col=1
            )
            
            # Add secondary DEM difference if available
            if has_multi_dem:
                diff2 = profile1_dem2['elevations'] - profile2_dem2['elevations']
                fig.add_trace(
                    go.Scatter(
                        x=profile1_dem2['distances'], 
                        y=diff2,
                        mode='lines',
                        name=f'Difference ({self.profile_data["dem2_name"]})',
                        line=dict(color='orange', width=2, dash='dash'),
                        hovertemplate='Distance: %{x:.2f}m<br>Difference: %{y:.3f}m<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            # Add zero line
            fig.add_trace(
                go.Scatter(
                    x=[profile1['distances'][0], profile1['distances'][-1]],
                    y=[0, 0],
                    mode='lines',
                    line=dict(color='black', width=1, dash='dash'),
                    name='Zero line',
                    showlegend=False,
                    hoverinfo='skip'
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_xaxes(title_text="Distance (m)", row=1, col=1, showgrid=True)
            fig.update_xaxes(title_text="Distance (m)", row=2, col=1, showgrid=True)
            fig.update_yaxes(title_text="Elevation (m)", row=1, col=1, showgrid=True)
            fig.update_yaxes(title_text="Elevation Difference (m)", row=2, col=1, showgrid=True)
            
            fig.update_layout(
                height=600,
                showlegend=True,
                hovermode='x unified',
                template='plotly_white'
            )
            
            # Store figure
            self.current_figure = fig
            
            # Open in browser
            self.open_graph_in_browser(fig)
            
        # Calculate statistics
        if has_multi_dem:
            self.calculate_statistics_multi(profile1, profile2, profile1_dem2, profile2_dem2)
        else:
            self.calculate_statistics(profile1, profile2)
    
    def open_graph_in_browser(self, fig):
        """Open graph in browser"""
        temp_html = os.path.join(tempfile.gettempdir(), f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        fig.write_html(temp_html, auto_open=True)
        
        self.info_text.setText(
            f"📊 INTERACTIVE GRAPH OPENED IN BROWSER\n"
            f"File: {temp_html}\n\n"
            f"Use the browser's tools to interact with the graph."
        )
    
    def calculate_statistics(self, profile1, profile2):
        """Calculate and show statistics"""
        diff = profile1['elevations'] - profile2['elevations']
        valid_diff = diff[~np.isnan(diff)]
        
        if len(valid_diff) > 0:
            stats_text = f"""📊 PROFILE STATISTICS:
━━━━━━━━━━━━━━━━━━━━━
Profile A-A' (Upper):
  • Min: {np.nanmin(profile1['elevations']):.3f} m
  • Max: {np.nanmax(profile1['elevations']):.3f} m
  • Mean: {np.nanmean(profile1['elevations']):.3f} m

Profile B-B' (Lower):
  • Min: {np.nanmin(profile2['elevations']):.3f} m
  • Max: {np.nanmax(profile2['elevations']):.3f} m
  • Mean: {np.nanmean(profile2['elevations']):.3f} m

Difference (A-B):
  • Min: {np.min(valid_diff):.3f} m
  • Max: {np.max(valid_diff):.3f} m
  • Mean: {np.mean(valid_diff):.3f} m

Section length: {profile1['distances'][-1]:.2f} m
Offset: {self.spin_distance.value():.2f} m
            """
        else:
            stats_text = "No valid data extracted"
            
        self.info_text.setText(stats_text)
    
    def calculate_statistics_multi(self, profile1, profile2, profile1_dem2, profile2_dem2):
        """Calculate and show statistics for multiple DEMs"""
        diff1 = profile1['elevations'] - profile2['elevations']
        diff2 = profile1_dem2['elevations'] - profile2_dem2['elevations']
        
        # Remove NaN for statistics
        valid_diff1 = diff1[~np.isnan(diff1)]
        valid_diff2 = diff2[~np.isnan(diff2)]
        
        # DEM differences
        dem_diff_a = profile1['elevations'] - profile1_dem2['elevations']
        dem_diff_b = profile2['elevations'] - profile2_dem2['elevations']
        valid_dem_diff_a = dem_diff_a[~np.isnan(dem_diff_a)]
        valid_dem_diff_b = dem_diff_b[~np.isnan(dem_diff_b)]
        
        stats_text = f"""📊 MULTI-DEM COMPARISON:
━━━━━━━━━━━━━━━━━━━━━
{self.profile_data['dem1_name']}:
  A-A': Min={np.nanmin(profile1['elevations']):.3f}, Max={np.nanmax(profile1['elevations']):.3f}, Mean={np.nanmean(profile1['elevations']):.3f}
  B-B': Min={np.nanmin(profile2['elevations']):.3f}, Max={np.nanmax(profile2['elevations']):.3f}, Mean={np.nanmean(profile2['elevations']):.3f}
  Diff: Min={np.min(valid_diff1) if len(valid_diff1) > 0 else 0:.3f}, Max={np.max(valid_diff1) if len(valid_diff1) > 0 else 0:.3f}, Mean={np.mean(valid_diff1) if len(valid_diff1) > 0 else 0:.3f}

{self.profile_data['dem2_name']}:
  A-A': Min={np.nanmin(profile1_dem2['elevations']):.3f}, Max={np.nanmax(profile1_dem2['elevations']):.3f}, Mean={np.nanmean(profile1_dem2['elevations']):.3f}
  B-B': Min={np.nanmin(profile2_dem2['elevations']):.3f}, Max={np.nanmax(profile2_dem2['elevations']):.3f}, Mean={np.nanmean(profile2_dem2['elevations']):.3f}
  Diff: Min={np.min(valid_diff2) if len(valid_diff2) > 0 else 0:.3f}, Max={np.max(valid_diff2) if len(valid_diff2) > 0 else 0:.3f}, Mean={np.mean(valid_diff2) if len(valid_diff2) > 0 else 0:.3f}

DEM Comparison:
  A-A' difference: Mean={np.mean(valid_dem_diff_a) if len(valid_dem_diff_a) > 0 else 0:.3f}m, StdDev={np.std(valid_dem_diff_a) if len(valid_dem_diff_a) > 0 else 0:.3f}m
  B-B' difference: Mean={np.mean(valid_dem_diff_b) if len(valid_dem_diff_b) > 0 else 0:.3f}m, StdDev={np.std(valid_dem_diff_b) if len(valid_dem_diff_b) > 0 else 0:.3f}m

Section: {profile1['distances'][-1]:.2f}m, Points: {len(profile1['distances'])}, Offset: {self.spin_distance.value():.2f}m
        """
        
        self.info_text.setText(stats_text)
        
    def create_section_layer(self):
        """Create a vector layer with section lines"""
        if not self.profile_data:
            return
            
        self.section_count += 1
        
        # Create or get existing layer
        layer_name = "Profile_Sections"
        layers = QgsProject.instance().mapLayersByName(layer_name)
        
        if layers:
            section_layer = layers[0]
        else:
            # Create new layer
            crs = QgsProject.instance().crs()
            section_layer = QgsVectorLayer(
                f"LineString?crs={crs.authid()}&field=id:integer&field=label:string&field=type:string",
                layer_name,
                "memory"
            )
            
            QgsProject.instance().addMapLayer(section_layer)
        
        # Add features
        section_layer.startEditing()
        
        # Add line A-A'
        feature1 = QgsFeature()
        feature1.setGeometry(QgsGeometry.fromPolylineXY(self.profile_data['line1']))
        feature1.setAttributes([
            self.section_count * 2 - 1,
            f"A{self.section_count}-A'{self.section_count}",
            "Upper"
        ])
        section_layer.addFeature(feature1)
        
        # Add line B-B'
        feature2 = QgsFeature()
        feature2.setGeometry(QgsGeometry.fromPolylineXY(self.profile_data['line2']))
        feature2.setAttributes([
            self.section_count * 2,
            f"B{self.section_count}-B'{self.section_count}",
            "Lower"
        ])
        section_layer.addFeature(feature2)
        
        section_layer.commitChanges()
        
        # Apply symbology
        self.setup_layer_symbology(section_layer)
        
        self.iface.mapCanvas().refresh()
        
        QtWidgets.QMessageBox.information(
            self,
            "Success",
            f"✅ Section lines created"
        )
        
    def setup_layer_symbology(self, layer):
        """Set up symbology"""
        categories = []
        
        # Red for Upper
        symbol_upper = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol_upper.setColor(QColor(255, 0, 0))
        symbol_upper.setWidth(1.5)
        cat_upper = QgsRendererCategory('Upper', symbol_upper, "A-A'")
        categories.append(cat_upper)
        
        # Blue for Lower
        symbol_lower = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol_lower.setColor(QColor(0, 0, 255))
        symbol_lower.setWidth(1.5)
        cat_lower = QgsRendererCategory('Lower', symbol_lower, "B-B'")
        categories.append(cat_lower)
        
        renderer = QgsCategorizedSymbolRenderer('type', categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
    
    def export_vector_profile(self):
        """Export profile as georeferenced vector"""
        if not self.profile_data:
            QtWidgets.QMessageBox.warning(self, "Warning", 
                                         "No profile data to export!")
            return
        
        # Show options dialog
        dialog = VectorExportDialog(self)
        if dialog.exec_():
            options = dialog.get_options()
            
            # Check if we should include secondary DEM profiles
            include_dem2 = False
            if self.profile_data.get('profile1_dem2') is not None:
                # Check if secondary DEM has valid data
                valid_count = np.sum(~np.isnan(self.profile_data['profile1_dem2']['elevations']))
                if valid_count > 0:
                    include_dem2 = True
                    
                    # Ask user if they want to export both DEMs
                    reply = QtWidgets.QMessageBox.question(
                        self,
                        "Export Multiple DEMs",
                        "You have compared two DEMs.\n\n"
                        "Do you want to export profiles from both DEMs?\n"
                        "Yes = Export both\n"
                        "No = Export primary DEM only",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                    )
                    
                    if reply == QtWidgets.QMessageBox.No:
                        include_dem2 = False
            
            # Get output file
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save profile as vector",
                f"profile_vector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gpkg",
                "GeoPackage (*.gpkg);;Shapefile (*.shp)"
            )
            
            if filename:
                try:
                    # Handle 3D export separately
                    if options['type'] == '3d':
                        layer = ProfileExporter.export_profiles_as_3d_vector(
                            self.profile_data,
                            filename,
                            add_to_map=options['add_to_map']
                        )
                    else:
                        # For 2D export, handle multiple DEMs
                        if include_dem2:
                            # Export primary DEM
                            base_name = os.path.splitext(filename)[0]
                            ext = os.path.splitext(filename)[1]
                            
                            # Create filenames for each DEM
                            filename1 = f"{base_name}_DEM1{ext}"
                            filename2 = f"{base_name}_DEM2{ext}"
                            
                            # Export primary DEM profiles
                            profile_data_dem1 = {
                                'profile1': self.profile_data['profile1'],
                                'profile2': self.profile_data['profile2'],
                                'line1': self.profile_data['line1'],
                                'line2': self.profile_data['line2']
                            }
                            
                            layer1 = ProfileExporter.export_profile_as_vector(
                                profile_data_dem1,
                                filename1,
                                export_type=options['type'],
                                scale_factor=options['scale'],
                                vertical_exaggeration=options['vertical_exag'],
                                baseline_offset=options['baseline_offset'],
                                add_to_map=options['add_to_map']
                            )
                            
                            # Export secondary DEM profiles
                            profile_data_dem2 = {
                                'profile1': self.profile_data['profile1_dem2'],
                                'profile2': self.profile_data['profile2_dem2'],
                                'line1': self.profile_data['line1'],
                                'line2': self.profile_data['line2']
                            }
                            
                            layer2 = ProfileExporter.export_profile_as_vector(
                                profile_data_dem2,
                                filename2,
                                export_type=options['type'],
                                scale_factor=options['scale'],
                                vertical_exaggeration=options['vertical_exag'],
                                baseline_offset=options['baseline_offset'],
                                add_to_map=options['add_to_map']
                            )
                            
                            QtWidgets.QMessageBox.information(
                                self, "Success",
                                f"✅ Profiles exported from both DEMs:\n"
                                f"DEM1: {filename1}\n"
                                f"DEM2: {filename2}\n\n"
                                f"The profile shapes have been preserved as georeferenced features."
                            )
                        else:
                            # Export single DEM
                            layer = ProfileExporter.export_profile_as_vector(
                                self.profile_data,
                                filename,
                                export_type=options['type'],
                                scale_factor=options['scale'],
                                vertical_exaggeration=options['vertical_exag'],
                                baseline_offset=options['baseline_offset'],
                                add_to_map=options['add_to_map']
                            )
                            
                            QtWidgets.QMessageBox.information(
                                self, "Success",
                                f"✅ Profile exported as vector:\n{filename}\n\n"
                                f"The profile shape has been preserved as a georeferenced feature."
                            )
                    
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self, "Error", f"Export failed:\n{str(e)}"
                    )
    
    def export_data(self):
        """Export profile data to CSV"""
        if not self.profile_data:
            return
            
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save profiles",
            f"profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                import csv
                
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    header = [
                        'Distance_m', 'X', 'Y',
                        'Elevation_A_m', 'Elevation_B_m',
                        'Difference_m', 'Offset_m'
                    ]
                    writer.writerow(header)
                    
                    # Data
                    p1 = self.profile_data['profile1']
                    p2 = self.profile_data['profile2']
                    
                    for i in range(len(p1['distances'])):
                        row = [
                            p1['distances'][i],
                            p1['x_coords'][i],
                            p1['y_coords'][i],
                            p1['elevations'][i],
                            p2['elevations'][i],
                            p1['elevations'][i] - p2['elevations'][i],
                            self.profile_data['offset']
                        ]
                        writer.writerow(row)
                        
                QtWidgets.QMessageBox.information(
                    self, "Success",
                    f"Data exported to:\n{filename}"
                )
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error",
                    f"Export error:\n{str(e)}"
                )
    
    def show_help(self):
        """Open the user manual"""
        import os
        import webbrowser
        from pathlib import Path
        
        # Get the plugin directory
        plugin_dir = os.path.dirname(__file__)
        manual_path = os.path.join(plugin_dir, "USER_MANUAL.md")
        
        # Check if manual exists
        if os.path.exists(manual_path):
            # Try to open with system default markdown viewer
            # On most systems, this will open in the default browser or markdown editor
            try:
                # Convert to file URL
                file_url = Path(manual_path).as_uri()
                webbrowser.open(file_url)
            except Exception:
                # If that fails, try to open directly
                try:
                    import subprocess
                    if os.name == 'nt':  # Windows
                        os.startfile(manual_path)
                    elif os.name == 'posix':  # macOS and Linux
                        subprocess.call(['open', manual_path])
                except Exception as e:
                    # Last resort: show path to user
                    QtWidgets.QMessageBox.information(
                        self,
                        "User Manual",
                        f"User manual is located at:\n\n{manual_path}\n\n"
                        f"Please open it with your preferred markdown viewer."
                    )
        else:
            # Manual not found, offer to open online version
            reply = QtWidgets.QMessageBox.question(
                self,
                "User Manual",
                "Local manual not found.\n\n"
                "Would you like to open the online documentation?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                webbrowser.open("https://github.com/enzococca/dual-profile-viewer/wiki")
    
    def open_3d_viewer(self):
        """Open the 3D viewer with current profile data"""
        if not self.profile_data:
            QtWidgets.QMessageBox.warning(self, "No Data", 
                                         "Please create profiles first before opening 3D viewer")
            return
        
        # Import the 3D viewer
        from .advanced_3d_viewer import Advanced3DViewer
        
        # Create viewer if not exists
        if not hasattr(self, 'viewer_3d') or self.viewer_3d is None:
            self.viewer_3d = Advanced3DViewer(self)
        
        # Prepare profile data list with proper format
        self.prepare_profile_data_for_3d()
        
        # Load profiles into viewer
        if self.profile_data_list:
            self.viewer_3d.load_profiles(self.profile_data_list)
        
        # Show the viewer
        self.viewer_3d.show()
    
    def prepare_profile_data_for_3d(self):
        """Prepare profile data in format needed for 3D viewer"""
        self.profile_data_list = []
        
        if not self.profile_data:
            return
        
        # Prepare profile 1
        if 'profile1' in self.profile_data:
            p1 = self.profile_data['profile1']
            profile1_data = {
                'name': 'Profile A (Red)',
                'distances': p1['distances'],
                'elevations': p1['elevations'],
                'coordinates': list(zip(p1['x_coords'], p1['y_coords'])) if 'x_coords' in p1 else None
            }
            self.profile_data_list.append(profile1_data)
        
        # Prepare profile 2
        if 'profile2' in self.profile_data:
            p2 = self.profile_data['profile2']
            profile2_data = {
                'name': 'Profile B (Blue)',
                'distances': p2['distances'],
                'elevations': p2['elevations'],
                'coordinates': list(zip(p2['x_coords'], p2['y_coords'])) if 'x_coords' in p2 else None
            }
            self.profile_data_list.append(profile2_data)
    
    def get_profile_data(self):
        """Get profile data for 3D visualization"""
        if not self.profile_data:
            return None
            
        # Return combined profile data suitable for stratigraph
        profile_points = []
        
        # Use profile 1 as the main profile
        p1 = self.profile_data['profile1']
        for i in range(len(p1['distances'])):
            if not np.isnan(p1['elevations'][i]):
                profile_points.append((
                    p1['distances'][i],
                    p1['elevations'][i],
                    0  # Z coordinate for 2D profile
                ))
                
        return profile_points
        
    def get_all_profile_data(self):
        """Get all profile data for cross-section visualization"""
        if not self.profile_data:
            return []
            
        all_profiles = []
        
        # Get both profiles
        for profile_key in ['profile1', 'profile2']:
            if profile_key in self.profile_data:
                profile = self.profile_data[profile_key]
                profile_points = []
                
                for i in range(len(profile['distances'])):
                    if not np.isnan(profile['elevations'][i]):
                        profile_points.append((
                            profile['distances'][i],
                            profile['elevations'][i],
                            0
                        ))
                        
                if profile_points:
                    all_profiles.append(profile_points)
                    
        return all_profiles