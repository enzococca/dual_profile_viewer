# -*- coding: utf-8 -*-
"""
Compact Dual Profile Viewer - Complete integrated version
Combines all functionality from the original dialog in a compact tabbed interface
"""

from qgis.PyQt import QtWidgets, QtCore
from qgis.PyQt.QtGui import QColor, QFont, QIcon
from qgis.PyQt.QtCore import Qt, QUrl, pyqtSignal
from qgis.PyQt.QtWidgets import (QTabWidget, QVBoxLayout, QHBoxLayout, 
                                QWidget, QSplitter, QGroupBox, QToolButton,
                                QSizePolicy, QFormLayout, QLabel)

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPoint, QgsPointXY, QgsLineString, QgsWkbTypes,
    QgsField, QgsFields, QgsVectorFileWriter,
    QgsCoordinateTransform, QgsCoordinateReferenceSystem,
    QgsRasterLayer, QgsRaster,
    QgsSymbol, QgsSimpleLineSymbolLayer,
    QgsSingleSymbolRenderer, QgsMarkerSymbol,
    QgsSimpleMarkerSymbolLayer,
    QgsCategorizedSymbolRenderer, QgsRendererCategory,
    QgsTextFormat, QgsVectorLayerSimpleLabeling,
    QgsPalLayerSettings, QgsTextBufferSettings,
    Qgis, QgsMessageLog
)
from qgis.gui import QgsMapTool, QgsRubberBand, QgsMapToolEmitPoint

import math
import numpy as np
from datetime import datetime
import os
import tempfile

# Try to import matplotlib
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
import webbrowser

# Import supporting modules
from .profile_exporter import ProfileExporter
from .vector_export_dialog import VectorExportDialog
from .multi_dem_widget import MultiDEMWidget

# Try to import QWebEngineView
try:
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    try:
        from qgis.PyQt.QtWebKitWidgets import QWebView as QWebEngineView
        WEBENGINE_AVAILABLE = True
    except ImportError:
        WEBENGINE_AVAILABLE = False

# Try to import plotly
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Import the drawing tool
from .dual_profile_tool import DualProfileTool


class CompactDualProfileViewer(QtWidgets.QWidget):
    """Complete compact dual profile viewer with all functionality"""
    
    profile_created = pyqtSignal(dict)
    
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.map_tool = None
        self.profile_data = None
        self.profile_data_list = []
        self.selected_dem_layers = []
        self.web_view = None
        self.lines_drawn = None
        self.section_count = 0
        self.plot_info = None  # For text fallback
        self.polygon_tool = None
        self.polygon_width = None
        self.section_polygon = None
        
        # Store all sections data for layout
        self.all_sections = []  # List of all section data with plots
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create compact tabbed interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create splitter for top controls and bottom plot
        splitter = QSplitter(Qt.Vertical)
        
        # Top part: toolbar and tabs
        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Compact toolbar
        toolbar = self.create_compact_toolbar()
        top_layout.addWidget(toolbar)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Profile Settings
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Tab 2: DEM Selection
        self.dem_tab = self.create_dem_tab()
        self.tab_widget.addTab(self.dem_tab, "DEMs")
        
        # Tab 3: Export Options
        self.export_tab = self.create_export_tab()
        self.tab_widget.addTab(self.export_tab, "Export")
        
        # Tab 4: Info/Stats
        self.info_tab = self.create_info_tab()
        self.tab_widget.addTab(self.info_tab, "Info")
        
        top_layout.addWidget(self.tab_widget)
        top_widget.setLayout(top_layout)
        splitter.addWidget(top_widget)
        
        # Bottom part: Plot view
        self.plot_widget = QWidget()
        plot_layout = QVBoxLayout()
        
        # Add buttons for plot options
        plot_toolbar = QtWidgets.QToolBar()
        plot_toolbar.setIconSize(QtCore.QSize(20, 20))
        
        self.use_web_action = plot_toolbar.addAction("🌐 Web View")
        self.use_web_action.setCheckable(True)
        self.use_web_action.setChecked(WEBENGINE_AVAILABLE)
        self.use_web_action.triggered.connect(self.toggle_plot_mode)
        
        self.open_browser_action = plot_toolbar.addAction("🔗 Open in Browser")
        self.open_browser_action.triggered.connect(self.open_in_browser)
        self.open_browser_action.setEnabled(False)
        
        plot_layout.addWidget(plot_toolbar)
        
        # Create stacked widget for different plot views
        from qgis.PyQt.QtWidgets import QStackedWidget
        self.plot_stack = QStackedWidget()
        
        # Web view
        if WEBENGINE_AVAILABLE and PLOTLY_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setMinimumHeight(300)
            self.plot_stack.addWidget(self.web_view)
            self.show_welcome_plot()
        else:
            self.web_view = None
            
        # Matplotlib view
        if MATPLOTLIB_AVAILABLE:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            self.figure = Figure(figsize=(8, 6))
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMinimumHeight(300)
            self.plot_stack.addWidget(self.canvas)
        else:
            # Fallback text view
            self.canvas = QtWidgets.QTextEdit()
            self.canvas.setReadOnly(True)
            self.canvas.setMinimumHeight(300)
            self.plot_stack.addWidget(self.canvas)
            self.figure = None
        
        # Set initial view
        if self.web_view:
            self.plot_stack.setCurrentWidget(self.web_view)
        else:
            self.plot_stack.setCurrentWidget(self.canvas)
            self.use_web_action.setChecked(False)
        
        plot_layout.addWidget(self.plot_stack)
        self.plot_widget.setLayout(plot_layout)
        splitter.addWidget(self.plot_widget)
        
        # Set splitter sizes (40% top, 60% bottom)
        splitter.setSizes([250, 350])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_compact_toolbar(self):
        """Create compact toolbar with essential actions"""
        toolbar = QtWidgets.QToolBar()
        toolbar.setIconSize(QtCore.QSize(24, 24))
        
        # Draw single line action
        self.draw_single_action = toolbar.addAction("➖ Single Line")
        self.draw_single_action.setToolTip("Draw single profile line")
        self.draw_single_action.triggered.connect(self.start_single_drawing)
        
        # Draw dual lines action
        self.draw_action = toolbar.addAction("📏 Dual Lines")
        self.draw_action.setToolTip("Draw dual profile lines")
        self.draw_action.triggered.connect(self.start_drawing)
        
        # Draw polygon
        self.draw_polygon_action = toolbar.addAction("⬜ Draw Polygon")
        self.draw_polygon_action.setToolTip("Draw profile polygon with width")
        self.draw_polygon_action.triggered.connect(self.start_polygon_drawing)
        
        toolbar.addSeparator()
        
        # Create profiles action
        self.create_action = toolbar.addAction("📊 Create Profiles")
        self.create_action.setToolTip("Extract elevation profiles")
        self.create_action.triggered.connect(self.create_profiles)
        self.create_action.setEnabled(False)
        
        # Create layer action
        self.layer_action = toolbar.addAction("📍 Create Layer")
        self.layer_action.setToolTip("Create section lines as vector layer")
        self.layer_action.triggered.connect(self.create_section_layer)
        self.layer_action.setEnabled(False)
        
        toolbar.addSeparator()
        
        # Export actions
        self.export_csv_action = toolbar.addAction("📄 CSV")
        self.export_csv_action.setToolTip("Export as CSV")
        self.export_csv_action.triggered.connect(self.export_csv)
        self.export_csv_action.setEnabled(False)
        
        self.export_vector_action = toolbar.addAction("📐 Vector")
        self.export_vector_action.setToolTip("Export as vector")
        self.export_vector_action.triggered.connect(self.export_vector_profile)
        self.export_vector_action.setEnabled(False)
        
        toolbar.addSeparator()
        
        # 3D view
        self.view3d_action = toolbar.addAction("🎲 3D View")
        self.view3d_action.setToolTip("Open 3D viewer")
        self.view3d_action.triggered.connect(self.open_3d_viewer)
        self.view3d_action.setEnabled(False)
        
        toolbar.addSeparator()
        
        # Clear
        self.clear_action = toolbar.addAction("🗑️ Clear")
        self.clear_action.setToolTip("Clear current profiles")
        self.clear_action.triggered.connect(self.clear_profiles)
        
        # Help
        self.help_action = toolbar.addAction("❓ Help")
        self.help_action.setToolTip("Show help")
        self.help_action.triggered.connect(self.show_help)
        
        toolbar.addSeparator()
        
        # Layout generator
        self.layout_action = toolbar.addAction("🖨️ Generate Layout")
        self.layout_action.setToolTip("Generate professional print layout")
        self.layout_action.triggered.connect(self.generate_layout)
        self.layout_action.setEnabled(False)
        
        # AI Report (optional)
        self.ai_report_action = toolbar.addAction("🤖 AI Report")
        self.ai_report_action.setToolTip("Generate AI analysis report")
        self.ai_report_action.triggered.connect(self.generate_ai_report)
        self.ai_report_action.setEnabled(False)
        
        return toolbar
        
    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Primary DEM selection
        dem_group = QGroupBox("Primary DEM/DTM")
        dem_layout = QVBoxLayout()
        
        self.combo_dem = QtWidgets.QComboBox()
        self.load_raster_layers()
        dem_layout.addWidget(self.combo_dem)
        
        dem_group.setLayout(dem_layout)
        layout.addWidget(dem_group)
        
        # Profile parameters
        params_group = QGroupBox("Profile Parameters")
        params_layout = QFormLayout()
        
        # Offset
        self.spin_distance = QtWidgets.QDoubleSpinBox()
        self.spin_distance.setMinimum(0.05)
        self.spin_distance.setMaximum(500.0)
        self.spin_distance.setValue(1.0)
        self.spin_distance.setSingleStep(0.05)
        self.spin_distance.setDecimals(2)
        self.spin_distance.setSuffix(" m")
        params_layout.addRow("Offset:", self.spin_distance)
        
        # Samples
        self.spin_samples = QtWidgets.QSpinBox()
        self.spin_samples.setMinimum(10)
        self.spin_samples.setMaximum(2000)
        self.spin_samples.setValue(200)
        params_layout.addRow("Samples:", self.spin_samples)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_dem_tab(self):
        """Create DEM selection tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Multi-DEM comparison
        self.check_multi_dem = QtWidgets.QCheckBox("Compare Multiple DEMs")
        self.check_multi_dem.toggled.connect(self.on_multi_dem_toggled)
        layout.addWidget(self.check_multi_dem)
        
        # Multi-DEM widget
        self.multi_dem_widget = MultiDEMWidget()
        self.multi_dem_widget.setVisible(False)
        self.multi_dem_widget.selection_changed.connect(self.on_dem_selection_changed)
        layout.addWidget(self.multi_dem_widget)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_export_tab(self):
        """Create export options tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Export info
        info_label = QLabel("Export profiles in various formats:")
        layout.addWidget(info_label)
        
        # Export buttons
        self.export_csv_btn = QtWidgets.QPushButton("📄 Export as CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.export_csv_btn.setEnabled(False)
        layout.addWidget(self.export_csv_btn)
        
        self.export_vector_btn = QtWidgets.QPushButton("📐 Export as Vector (Shapefile/GeoPackage)")
        self.export_vector_btn.clicked.connect(self.export_vector_profile)
        self.export_vector_btn.setEnabled(False)
        layout.addWidget(self.export_vector_btn)
        
        self.export_png_btn = QtWidgets.QPushButton("🖼️ Export Plot as Image")
        self.export_png_btn.clicked.connect(self.export_png)
        self.export_png_btn.setEnabled(False)
        layout.addWidget(self.export_png_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_info_tab(self):
        """Create info/statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info text
        self.info_text = QtWidgets.QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.info_text)
        
        widget.setLayout(layout)
        return widget
        
    def load_raster_layers(self):
        """Load available raster layers"""
        self.combo_dem.clear()
        
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsRasterLayer) and layer.isValid():
                self.combo_dem.addItem(layer.name(), layer.id())
                
        if self.combo_dem.count() == 0:
            self.combo_dem.addItem("(No DEM/DTM found)", None)
            
    def on_multi_dem_toggled(self, checked):
        """Toggle multi-DEM widget visibility"""
        self.multi_dem_widget.setVisible(checked)
        if checked:
            self.multi_dem_widget.refresh_dem_list()
            
    def on_dem_selection_changed(self, selected_layers):
        """Handle changes in DEM selection"""
        self.selected_dem_layers = selected_layers
        
    def start_single_drawing(self):
        """Activate single line drawing tool"""
        if self.combo_dem.currentData() is None:
            QtWidgets.QMessageBox.warning(self, "Warning", 
                                         "Please select a DEM/DTM layer first!")
            return
            
        # Create and activate single line tool
        from .single_profile_tool import SingleProfileTool
        self.map_tool = SingleProfileTool(self.iface.mapCanvas(), self.iface)
        self.map_tool.profile_created.connect(self.on_single_line_drawn)
        self.iface.mapCanvas().setMapTool(self.map_tool)
        
        # Update UI
        self.draw_single_action.setEnabled(False)
        self.draw_action.setEnabled(False)
        self.create_action.setEnabled(True)
        
    def start_drawing(self):
        """Activate drawing tool"""
        if self.combo_dem.currentData() is None:
            QtWidgets.QMessageBox.warning(self, "Warning", 
                                         "Please select a DEM/DTM layer first!")
            return
            
        # Create and activate map tool
        self.map_tool = DualProfileTool(self.iface.mapCanvas(), self.on_lines_drawn)
        self.map_tool.offset_distance = self.spin_distance.value()
        self.iface.mapCanvas().setMapTool(self.map_tool)
        
        # Update UI
        self.draw_action.setEnabled(False)
        self.draw_single_action.setEnabled(False)
        self.create_action.setEnabled(True)
        
        # Show status
        self.iface.messageBar().pushMessage(
            "Drawing", 
            "Click to set start point, click again to set end point",
            level=Qgis.Info,
            duration=5
        )
        
    def on_single_line_drawn(self, line):
        """Handle completion of single line drawing"""
        # Store as single line (no second line)
        self.lines_drawn = (line, None, line)  # line1, None for line2, center_line
        
        # Enable create button
        self.create_action.setEnabled(True)
        
        # Reset tool
        self.iface.mapCanvas().unsetMapTool(self.map_tool)
        self.draw_single_action.setEnabled(True)
        self.draw_action.setEnabled(True)
        self.draw_polygon_action.setEnabled(True)
        
        # Show message
        QtWidgets.QMessageBox.information(self, "Drawing Complete", 
                                        "Single section drawn. Click '📊 Create' to generate elevation profile.")
    
    def on_lines_drawn(self, line1, line2, center_line):
        """Handle completion of line drawing"""
        self.lines_drawn = (line1, line2, center_line)
        
        # Enable create button
        self.create_action.setEnabled(True)
        
        # Reset tool
        self.iface.mapCanvas().unsetMapTool(self.map_tool)
        self.draw_single_action.setEnabled(True)
        self.draw_action.setEnabled(True)
        self.draw_polygon_action.setEnabled(True)
        
        # Show message
        QtWidgets.QMessageBox.information(self, "Drawing Complete", 
                                        "Sections drawn. Click '📊 Create' to generate elevation profiles.")
    
    def start_polygon_drawing(self):
        """Start drawing profile polygon"""
        from .polygon_profile_tool import PolygonProfileTool
        
        if self.map_tool:
            self.iface.mapCanvas().unsetMapTool(self.map_tool)
            
        # Get selected DEM
        dem_layer_id = self.combo_dem.currentData()
        if not dem_layer_id:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a DEM layer first")
            return
        
        # Ask for drawing mode
        modes = ['Rectangle', 'Polygon', 'Freehand']
        mode, ok = QtWidgets.QInputDialog.getItem(self, "Drawing Mode",
                                                 "Select drawing mode:", modes, 0, False)
        if not ok:
            return
            
        # Ask for width
        width, ok = QtWidgets.QInputDialog.getDouble(self, "Section Width",
                                                    "Enter section width (m):",
                                                    10.0, 1.0, 100.0, 1)
        if not ok:
            return
            
        self.polygon_tool = PolygonProfileTool(self.iface.mapCanvas(), self.iface)
        self.polygon_tool.set_drawing_mode(mode.lower())
        self.polygon_tool.set_width(width)
        self.polygon_tool.profile_created.connect(self.on_polygon_drawn)
        
        self.iface.mapCanvas().setMapTool(self.polygon_tool)
        
        # Disable draw buttons while drawing
        self.draw_action.setEnabled(False)
        self.draw_polygon_action.setEnabled(False)
    
    def on_polygon_drawn(self, polygon_data):
        """Handle completion of polygon drawing"""
        polygon = polygon_data['polygon']
        width = polygon_data['width']
        draw_type = polygon_data['type']
        
        if draw_type == 'polygon' and 'sections' in polygon_data:
            # Multiple sections from polygon sides
            sections = polygon_data['sections']
            message = f"Polygon drawn with {len(sections)} sections, each {width}m wide."
            
            # Store all sections for processing
            self.polygon_sections = sections
            self.polygon_mode = True
            self.multi_section_mode = True
            
            # Store polygon data for multi-section processing
            self.polygon_data_full = polygon_data
        else:
            # Single section (rectangle or freehand)
            center_line = polygon_data['center_line']
            
            # Convert center line to points
            if center_line.isMultipart():
                points = center_line.asMultiPolyline()[0]
            else:
                points = center_line.asPolyline()
                
            if len(points) >= 2:
                self.lines_drawn = (points, points, points)
                
            message = f"Section drawn with {width}m width."
            self.polygon_mode = False
            self.multi_section_mode = False
            
        self.polygon_width = width
        self.section_polygon = polygon
        
        # Enable create button
        self.create_action.setEnabled(True)
        
        # Reset tool
        self.iface.mapCanvas().unsetMapTool(self.polygon_tool)
        self.draw_action.setEnabled(True)
        self.draw_single_action.setEnabled(True)
        self.draw_polygon_action.setEnabled(True)
        
        # Show message with polygon explanation
        info_text = message + "\n\nPolygon Mode Explanation:\n"
        info_text += "- Rectangle: Creates a single rectangular section\n"
        info_text += "- Polygon: Creates one section for each side of the polygon\n"
        info_text += "- Freehand: Creates a curved section following your drawing\n\n"
        info_text += "Click '📊 Create' to generate elevation profiles."
        
        QtWidgets.QMessageBox.information(self, "Drawing Complete", info_text)
        
    def create_profiles(self):
        """Create profiles from drawn lines"""
        if hasattr(self, 'multi_section_mode') and self.multi_section_mode and hasattr(self, 'polygon_data_full'):
            # Handle multiple sections from polygon
            self.extract_polygon_profiles()
        elif self.lines_drawn:
            line1, line2, center_line = self.lines_drawn
            self.extract_profiles(line1, line2, center_line)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No lines drawn yet. Please draw sections first.")
            
    def extract_profiles(self, line1, line2, center_line):
        """Extract elevation profiles along lines"""
        dem_layer_id = self.combo_dem.currentData()
        if not dem_layer_id:
            return
            
        dem_layer = QgsProject.instance().mapLayer(dem_layer_id)
        if not dem_layer:
            return
            
        num_samples = self.spin_samples.value()
        
        # Handle single line mode
        single_mode = line2 is None
        
        # Sample along lines
        if isinstance(line1, QgsGeometry):
            # Single line mode - extract points from geometry
            points = line1.asPolyline()
            if len(points) >= 2:
                profile1 = self.sample_raster_along_line(
                    dem_layer, points[0], points[1], num_samples
                )
            else:
                return
        else:
            # Dual line mode - line1 is a tuple of points
            profile1 = self.sample_raster_along_line(
                dem_layer, line1[0], line1[1], num_samples
            )
        
        # Only extract second profile if in dual mode
        if not single_mode:
            profile2 = self.sample_raster_along_line(
                dem_layer, line2[0], line2[1], num_samples
            )
        else:
            profile2 = None
        
        # Initialize variables for multi-DEM
        profile1_dem2 = None
        profile2_dem2 = None
        dem2_name = None
        additional_profiles = {}
        
        # Check for multiple DEMs
        if self.check_multi_dem.isChecked() and hasattr(self, 'selected_dem_layers'):
            for layer_id in self.selected_dem_layers:
                if layer_id == dem_layer.id():
                    continue  # Skip primary DEM
                    
                dem_layer_comp = QgsProject.instance().mapLayer(layer_id)
                if dem_layer_comp:
                    # For backward compatibility, store first comparison DEM separately
                    if profile1_dem2 is None:
                        dem2_name = dem_layer_comp.name()
                        if single_mode:
                            points = line1.asPolyline()
                            profile1_dem2 = self.sample_raster_along_line(
                                dem_layer_comp, points[0], points[1], num_samples
                            )
                            profile2_dem2 = None
                        else:
                            profile1_dem2 = self.sample_raster_along_line(
                                dem_layer_comp, line1[0], line1[1], num_samples
                            )
                            profile2_dem2 = self.sample_raster_along_line(
                                dem_layer_comp, line2[0], line2[1], num_samples
                            )
                    else:
                        # Store additional DEMs
                        if single_mode:
                            points = line1.asPolyline()
                            additional_profiles[dem_layer_comp.name()] = {
                                'profile1': self.sample_raster_along_line(
                                    dem_layer_comp, points[0], points[1], num_samples
                                ),
                                'profile2': None
                            }
                        else:
                            additional_profiles[dem_layer_comp.name()] = {
                                'profile1': self.sample_raster_along_line(
                                    dem_layer_comp, line1[0], line1[1], num_samples
                                ),
                                'profile2': self.sample_raster_along_line(
                                    dem_layer_comp, line2[0], line2[1], num_samples
                                )
                            }
        
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
            'dem2_name': dem2_name,
            'additional_profiles': additional_profiles,
            'section_number': self.section_count + 1,
            'single_mode': single_mode  # Flag to indicate single line mode
        }
        
        # Update profile list for 3D viewer
        self.profile_data_list = [profile1, profile2]
        if profile1_dem2:
            self.profile_data_list.extend([profile1_dem2, profile2_dem2])
        
        # Visualize
        self.plot_profiles()
        
        # Store this section data for layout (will store plot after visualization)
        section_data = {
            'profile_data': self.profile_data.copy(),
            'section_number': self.section_count + 1,
            'plot_html': None,  # Will be filled after plot creation
            'plot_image': None  # Will be filled if image is generated
        }
        self.all_sections.append(section_data)
        
        # Update statistics
        self.update_statistics()
        
        # Enable export buttons
        self.enable_export_buttons(True)
        
        # Enable 3D viewer
        self.view3d_action.setEnabled(True)
        
        # Enable layout generator
        self.layout_action.setEnabled(True)
        
        # Emit signal
        self.profile_created.emit(self.profile_data)
        
    def sample_raster_along_line(self, raster_layer, start_point, end_point, num_samples):
        """Sample raster along a line"""
        # Create interpolated points along line
        x_coords = np.linspace(start_point.x(), end_point.x(), num_samples)
        y_coords = np.linspace(start_point.y(), end_point.y(), num_samples)
        
        # Calculate progressive distances
        distances = np.zeros(num_samples)
        elevations = np.zeros(num_samples)
        
        # Get raster data provider
        provider = raster_layer.dataProvider()
        
        for i in range(num_samples):
            if i > 0:
                dx = x_coords[i] - x_coords[i-1]
                dy = y_coords[i] - y_coords[i-1]
                distances[i] = distances[i-1] + math.sqrt(dx*dx + dy*dy)
            
            # Sample elevation
            point = QgsPointXY(x_coords[i], y_coords[i])
            value, ok = provider.sample(point, 1)
            
            if ok and value is not None:
                elevations[i] = value
            else:
                elevations[i] = np.nan
        
        return {
            'distances': distances,
            'elevations': elevations,
            'x_coords': x_coords,
            'y_coords': y_coords
        }
        
    def plot_profiles(self):
        """Create and display plots"""
        # Enable browser button
        self.open_browser_action.setEnabled(True)
        
        # Check which view is active
        if self.use_web_action.isChecked() and self.web_view:
            # Use Plotly web view
            if PLOTLY_AVAILABLE:
                self.plot_with_plotly()
            else:
                self.plot_with_matplotlib()
        else:
            # Use matplotlib
            self.plot_with_matplotlib()
    
    def create_plotly_figure(self):
        """Create plotly figure from profile data"""
        if not self.profile_data:
            return None
            
        # Check if this is multi-section data
        if self.profile_data.get('multi_section', False):
            # Use multi-section plotting
            from .multi_section_handler import MultiSectionHandler
            return MultiSectionHandler.create_multi_section_plots(
                self.profile_data.get('sections', []), use_plotly=True
            )
            
        single_mode = self.profile_data.get('single_mode', False)
        
        if single_mode:
            # Single profile mode - simpler layout
            fig = make_subplots(
                rows=1, cols=1,
                subplot_titles=('Elevation Profile',)
            )
        else:
            # Dual profile mode - 4 graphs
            fig = make_subplots(
                rows=2, cols=2,
                shared_xaxes=True,
                vertical_spacing=0.15,
                horizontal_spacing=0.1,
                subplot_titles=('Overlapped Profiles', 'Elevation Differences',
                              'Profile A-A\'', 'Profile B-B\'')
            )
        
        # Plot primary DEM
        profile1 = self.profile_data['profile1']
        profile2 = self.profile_data['profile2']
        
        if single_mode:
            # Single profile plot
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'],
                    y=profile1['elevations'],
                    mode='lines',
                    name=f"Profile ({self.profile_data['dem1_name']})",
                    line=dict(color='red', width=2),
                    showlegend=True
                ),
                row=1, col=1
            )
        else:
            # Top left - Overlapped profiles
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'],
                    y=profile1['elevations'],
                    mode='lines',
                    name=f"A-A' ({self.profile_data['dem1_name']})",
                    line=dict(color='red', width=2),
                    showlegend=True
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
                    showlegend=True
                ),
                row=1, col=1
            )
        
        if not single_mode:
            # Bottom left - Profile A-A' individual
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'],
                    y=profile1['elevations'],
                    mode='lines',
                    name=f"A-A' ({self.profile_data['dem1_name']})",
                    line=dict(color='red', width=2),
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # Bottom right - Profile B-B' individual
            fig.add_trace(
                go.Scatter(
                    x=profile2['distances'],
                    y=profile2['elevations'],
                    mode='lines',
                    name=f"B-B' ({self.profile_data['dem1_name']})",
                    line=dict(color='blue', width=2),
                    showlegend=False
                ),
                row=2, col=2
            )
            
            # Top right - Elevation differences
            diff = profile1['elevations'] - profile2['elevations']
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'],
                    y=diff,
                    mode='lines',
                    name='A-A\' minus B-B\'',
                    line=dict(color='green', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0,255,0,0.2)'
                ),
                row=1, col=2
            )
        
        # Plot comparison DEMs if available
        if self.profile_data['profile1_dem2'] is not None:
            profile1_dem2 = self.profile_data['profile1_dem2']
            profile2_dem2 = self.profile_data['profile2_dem2']
            
            if single_mode:
                # Add comparison DEM to single plot
                fig.add_trace(
                    go.Scatter(
                        x=profile1_dem2['distances'],
                        y=profile1_dem2['elevations'],
                        mode='lines',
                        name=f"Profile ({self.profile_data['dem2_name']})",
                        line=dict(color='orange', width=2, dash='dash')
                    ),
                    row=1, col=1
                )
            else:
                # Add to overlapped view
                fig.add_trace(
                    go.Scatter(
                        x=profile1_dem2['distances'],
                        y=profile1_dem2['elevations'],
                        mode='lines',
                        name=f"A-A' ({self.profile_data['dem2_name']})",
                        line=dict(color='orange', width=2, dash='dash')
                    ),
                    row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=profile2_dem2['distances'],
                    y=profile2_dem2['elevations'],
                    mode='lines',
                    name=f"B-B' ({self.profile_data['dem2_name']})",
                    line=dict(color='lightgreen', width=2, dash='dash')
                ),
                row=1, col=1
            )
            
            # Add to individual views
            fig.add_trace(
                go.Scatter(
                    x=profile1_dem2['distances'],
                    y=profile1_dem2['elevations'],
                    mode='lines',
                    name=f"A-A' ({self.profile_data['dem2_name']})",
                    line=dict(color='orange', width=2, dash='dash'),
                    showlegend=False
                ),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=profile2_dem2['distances'],
                    y=profile2_dem2['elevations'],
                    mode='lines',
                    name=f"B-B' ({self.profile_data['dem2_name']})",
                    line=dict(color='lightgreen', width=2, dash='dash'),
                    showlegend=False
                ),
                row=2, col=2
            )
        
        # Plot additional DEMs
        if 'additional_profiles' in self.profile_data:
            colors = ['purple', 'brown', 'pink', 'gray', 'olive']
            color_idx = 0
            for dem_name, profiles in self.profile_data['additional_profiles'].items():
                color = colors[color_idx % len(colors)]
                
                fig.add_trace(
                    go.Scatter(
                        x=profiles['profile1']['distances'],
                        y=profiles['profile1']['elevations'],
                        mode='lines',
                        name=f"A-A' ({dem_name})",
                        line=dict(color=color, width=2, dash='dot')
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=profiles['profile2']['distances'],
                        y=profiles['profile2']['elevations'],
                        mode='lines',
                        name=f"B-B' ({dem_name})",
                        line=dict(color=color, width=2, dash='dot')
                    ),
                    row=2, col=1
                )
                color_idx += 1
        
        # Update layout
        fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
        fig.update_xaxes(title_text="Distance (m)", row=2, col=2)
        fig.update_yaxes(title_text="Elevation (m)", row=1, col=1)
        fig.update_yaxes(title_text="Difference (m)", row=1, col=2)
        fig.update_yaxes(title_text="Elevation (m)", row=2, col=1)
        fig.update_yaxes(title_text="Elevation (m)", row=2, col=2)
        
        fig.update_layout(
            height=600,
            showlegend=True,
            title_text="Elevation Profiles",
            hovermode='x unified'
        )
        
        return fig
    
    def plot_with_plotly(self):
        """Plot using Plotly in web view"""
        fig = self.create_plotly_figure()
        if not fig:
            return
            
        # Generate HTML
        html = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')
        full_html = f"""
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 5px; }}
                .plotly-graph-div {{ width: 100% !important; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Save HTML to current section
        if self.all_sections:
            self.all_sections[-1]['plot_html'] = full_html
            # Also generate image for layout
            self.generate_plot_image_for_section(self.all_sections[-1])
        
        # Load in web view
        try:
            self.web_view.setHtml(full_html)
        except Exception as e:
            # If web view fails, offer to open in browser
            reply = QtWidgets.QMessageBox.question(self, "WebView Error",
                f"Failed to display in widget: {str(e)}\n\nOpen in external browser instead?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.open_in_browser()
    
    def plot_with_matplotlib(self):
        """Plot using matplotlib"""
        if not self.profile_data:
            return
            
        if not MATPLOTLIB_AVAILABLE or not self.figure:
            # Use text fallback
            self.update_fallback_plot()
            return
            
        # Clear figure
        self.figure.clear()
        
        # Check if this is multi-section data
        if self.profile_data.get('multi_section', False):
            # Use multi-section plotting
            self.plot_multi_section_profiles()
            return
        
        # Check if single mode
        single_mode = self.profile_data.get('single_mode', False)
        profile1 = self.profile_data['profile1']
        profile2 = self.profile_data['profile2']
        
        if single_mode or profile2 is None:
            # Single profile plot
            ax = self.figure.add_subplot(1, 1, 1)
            
            ax.plot(profile1['distances'], profile1['elevations'], 
                     'r-', linewidth=2, label=f"Profile ({self.profile_data['dem1_name']})")
                     
            # Plot comparison DEMs if available
            if self.profile_data['profile1_dem2'] is not None:
                profile1_dem2 = self.profile_data['profile1_dem2']
                ax.plot(profile1_dem2['distances'], profile1_dem2['elevations'], 
                         'orange', linewidth=2, linestyle='--', 
                         label=f"Profile ({self.profile_data['dem2_name']})")
                         
            # Plot additional DEMs
            if 'additional_profiles' in self.profile_data:
                colors = ['purple', 'brown', 'pink', 'gray', 'olive']
                color_idx = 0
                for dem_name, profiles in self.profile_data['additional_profiles'].items():
                    if profiles['profile1'] is not None:
                        color = colors[color_idx % len(colors)]
                        ax.plot(profiles['profile1']['distances'], profiles['profile1']['elevations'],
                                 color=color, linewidth=2, linestyle=':',
                                 label=f"Profile ({dem_name})")
                        color_idx += 1
                        
            ax.set_xlabel('Distance (m)')
            ax.set_ylabel('Elevation (m)')
            ax.set_title('Elevation Profile')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
        else:
            # Dual profile plot
            ax1 = self.figure.add_subplot(2, 1, 1)
            ax2 = self.figure.add_subplot(2, 1, 2, sharex=ax1)
            
            ax1.plot(profile1['distances'], profile1['elevations'], 
                     'r-', linewidth=2, label=f"A-A' ({self.profile_data['dem1_name']})")
            ax2.plot(profile2['distances'], profile2['elevations'], 
                     'b-', linewidth=2, label=f"B-B' ({self.profile_data['dem1_name']})")
        
            # Plot comparison DEMs if available
            if self.profile_data['profile1_dem2'] is not None:
                profile1_dem2 = self.profile_data['profile1_dem2']
                profile2_dem2 = self.profile_data['profile2_dem2']
                
                ax1.plot(profile1_dem2['distances'], profile1_dem2['elevations'], 
                         'orange', linewidth=2, linestyle='--', 
                         label=f"A-A' ({self.profile_data['dem2_name']})")
                if profile2_dem2 is not None:
                    ax2.plot(profile2_dem2['distances'], profile2_dem2['elevations'], 
                             'green', linewidth=2, linestyle='--', 
                             label=f"B-B' ({self.profile_data['dem2_name']})")
        
            # Plot additional DEMs
            if 'additional_profiles' in self.profile_data:
                colors = ['purple', 'brown', 'pink', 'gray', 'olive']
                color_idx = 0
                for dem_name, profiles in self.profile_data['additional_profiles'].items():
                    color = colors[color_idx % len(colors)]
                    
                    if profiles['profile1'] is not None:
                        ax1.plot(profiles['profile1']['distances'], profiles['profile1']['elevations'],
                                 color=color, linewidth=2, linestyle=':',
                                 label=f"A-A' ({dem_name})")
                    if profiles['profile2'] is not None:
                        ax2.plot(profiles['profile2']['distances'], profiles['profile2']['elevations'],
                                 color=color, linewidth=2, linestyle=':',
                                 label=f"B-B' ({dem_name})")
                    color_idx += 1
            
            # Format axes
            ax1.set_ylabel('Elevation (m)')
            ax1.set_title('Profile A-A\'')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            
            ax2.set_xlabel('Distance (m)')
            ax2.set_ylabel('Elevation (m)')
            ax2.set_title('Profile B-B\'')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def update_statistics(self):
        """Update statistics in info tab"""
        if not self.profile_data:
            return
            
        # Check if this is multi-section data
        if self.profile_data.get('multi_section', False):
            # Use multi-section statistics
            self.update_multi_section_statistics()
            return
            
        profile1 = self.profile_data['profile1']
        profile2 = self.profile_data['profile2']
        single_mode = self.profile_data.get('single_mode', False)
        
        # Calculate statistics based on mode
        if single_mode or profile2 is None:
            # Single profile mode
            stats_text = f"""📊 PROFILE STATISTICS
━━━━━━━━━━━━━━━━━━
Primary DEM: {self.profile_data['dem1_name']}

Profile:
  Min: {np.nanmin(profile1['elevations']):.3f} m
  Max: {np.nanmax(profile1['elevations']):.3f} m
  Mean: {np.nanmean(profile1['elevations']):.3f} m

Section Length: {profile1['distances'][-1]:.2f} m
Number of Samples: {len(profile1['distances'])}
"""
        else:
            # Dual profile mode
            # Handle NaN values properly before subtraction
            mask1 = ~np.isnan(profile1['elevations'])
            mask2 = ~np.isnan(profile2['elevations'])
            valid_mask = mask1 & mask2  # Use bitwise AND instead of subtraction
            
            if np.any(valid_mask):
                diff = np.full_like(profile1['elevations'], np.nan)
                diff[valid_mask] = profile1['elevations'][valid_mask] - profile2['elevations'][valid_mask]
                valid_diff = diff[valid_mask]
            else:
                valid_diff = np.array([])
        
            stats_text = f"""📊 PROFILE STATISTICS
━━━━━━━━━━━━━━━━━━
Primary DEM: {self.profile_data['dem1_name']}

Profile A-A':
  Min: {np.nanmin(profile1['elevations']):.3f} m
  Max: {np.nanmax(profile1['elevations']):.3f} m
  Mean: {np.nanmean(profile1['elevations']):.3f} m

Profile B-B':
  Min: {np.nanmin(profile2['elevations']):.3f} m
  Max: {np.nanmax(profile2['elevations']):.3f} m
  Mean: {np.nanmean(profile2['elevations']):.3f} m

Difference (A-B):
  Min: {np.min(valid_diff) if len(valid_diff) > 0 else 0:.3f} m
  Max: {np.max(valid_diff) if len(valid_diff) > 0 else 0:.3f} m
  Mean: {np.mean(valid_diff) if len(valid_diff) > 0 else 0:.3f} m

Section Length: {profile1['distances'][-1]:.2f} m
Number of Samples: {len(profile1['distances'])}
Offset Distance: {self.spin_distance.value():.2f} m
"""
        
        # Add comparison DEM stats if available
        if self.profile_data['profile1_dem2'] is not None:
            profile1_dem2 = self.profile_data['profile1_dem2']
            profile2_dem2 = self.profile_data['profile2_dem2']
            
            if single_mode or profile2_dem2 is None:
                stats_text += f"""
━━━━━━━━━━━━━━━━━━
Comparison DEM: {self.profile_data['dem2_name']}

Profile:
  Min: {np.nanmin(profile1_dem2['elevations']):.3f} m
  Max: {np.nanmax(profile1_dem2['elevations']):.3f} m
  Mean: {np.nanmean(profile1_dem2['elevations']):.3f} m
"""
            else:
                stats_text += f"""
━━━━━━━━━━━━━━━━━━
Comparison DEM: {self.profile_data['dem2_name']}

Profile A-A':
  Min: {np.nanmin(profile1_dem2['elevations']):.3f} m
  Max: {np.nanmax(profile1_dem2['elevations']):.3f} m
  Mean: {np.nanmean(profile1_dem2['elevations']):.3f} m

Profile B-B':
  Min: {np.nanmin(profile2_dem2['elevations']):.3f} m
  Max: {np.nanmax(profile2_dem2['elevations']):.3f} m
  Mean: {np.nanmean(profile2_dem2['elevations']):.3f} m

DEM Difference (Primary - Comparison):
  A-A': {np.nanmean(profile1['elevations'] - profile1_dem2['elevations']) if profile1_dem2 is not None else 0:.3f} m
  B-B': {np.nanmean(profile2['elevations'] - profile2_dem2['elevations']) if profile2_dem2 is not None else 0:.3f} m
"""
        
        self.info_text.setText(stats_text)
        
    def show_welcome_plot(self):
        """Show welcome message in web view"""
        if not self.web_view or not PLOTLY_AVAILABLE:
            return
            
        fig = go.Figure()
        
        fig.add_annotation(
            text="<b>Dual Profile Viewer</b><br><br>Click '📏 Draw' to start creating elevation profiles",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16),
            align="center"
        )
        
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(240,240,240,0.5)'
        )
        
        html = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')
        full_html = f"""
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 10px; background-color: #f0f0f0; }}
                .plotly-graph-div {{ width: 100% !important; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        self.web_view.setHtml(full_html)
        
    def setup_fallback_plot(self):
        """Setup fallback when Plotly not available"""
        html_content = """
            <h3>Plotly Visualization</h3>
            <p>To enable integrated plots, install Plotly:</p>
            <pre>pip install plotly</pre>
            <p>Current status:</p>
            <ul>
            <li>Plotly: <b>Not installed</b></li>
            <li>WebEngine: <b>{}</b></li>
            </ul>
        """.format("Available" if WEBENGINE_AVAILABLE else "Not available")
        
        if isinstance(self.canvas, QtWidgets.QTextEdit):
            self.canvas.setHtml(html_content)
        elif self.plot_info:
            self.plot_info.setHtml(html_content)
        
    def update_fallback_plot(self):
        """Update fallback plot with text data"""
        if not self.profile_data:
            return
            
        text = "ELEVATION PROFILES\n"
        text += "=" * 50 + "\n\n"
        
        # Add profile data as text
        profile1 = self.profile_data['profile1']
        text += f"Profile A-A' ({self.profile_data['dem1_name']}):\n"
        text += f"  Points: {len(profile1['distances'])}\n"
        text += f"  Min Elevation: {np.nanmin(profile1['elevations']):.2f} m\n"
        text += f"  Max Elevation: {np.nanmax(profile1['elevations']):.2f} m\n\n"
        
        profile2 = self.profile_data['profile2']
        text += f"Profile B-B' ({self.profile_data['dem1_name']}):\n"
        text += f"  Points: {len(profile2['distances'])}\n"
        text += f"  Min Elevation: {np.nanmin(profile2['elevations']):.2f} m\n"
        text += f"  Max Elevation: {np.nanmax(profile2['elevations']):.2f} m\n"
        
        # Use the appropriate text widget
        if isinstance(self.canvas, QtWidgets.QTextEdit):
            self.canvas.setPlainText(text)
        elif self.plot_info:
            self.plot_info.setPlainText(text)
        
    def enable_export_buttons(self, enabled):
        """Enable/disable export buttons"""
        self.export_csv_action.setEnabled(enabled)
        self.export_vector_action.setEnabled(enabled)
        self.export_csv_btn.setEnabled(enabled)
        self.export_vector_btn.setEnabled(enabled)
        self.export_png_btn.setEnabled(enabled)
        self.layer_action.setEnabled(enabled)
        self.ai_report_action.setEnabled(enabled)
        
    def clear_profiles(self):
        """Clear current profiles"""
        self.profile_data = None
        self.profile_data_list = []
        self.lines_drawn = None
        self.all_sections = []  # Clear all stored sections
        self.section_count = 0  # Reset section count
        
        # Reset UI
        self.enable_export_buttons(False)
        self.view3d_action.setEnabled(False)
        self.create_action.setEnabled(False)
        self.info_text.clear()
        
        # Show welcome message
        if self.web_view:
            self.show_welcome_plot()
        else:
            self.setup_fallback_plot()
            
        # Clear map tool if active
        if self.map_tool:
            self.iface.mapCanvas().unsetMapTool(self.map_tool)
            self.map_tool = None
            
    def create_section_layer(self):
        """Create vector layer with section lines"""
        if not self.profile_data:
            return
            
        # Check if this is multi-section data
        if self.profile_data.get('multi_section'):
            # Create multi-section layer
            self.create_multi_section_layer()
            return
            
        self.section_count += 1
        
        # Check if we have multiple DEMs
        has_multi_dem = (self.profile_data.get('profile1_dem2') is not None or 
                        'additional_profiles' in self.profile_data)
        
        if has_multi_dem:
            # Create separate files for each DEM
            self.create_multi_dem_layers()
        else:
            # Create single layer
            self.create_single_section_layer()
    
    def create_single_section_layer(self):
        """Create a single layer for sections"""
        # Create or get existing layer
        layer_name = "Profile_Sections"
        layers = QgsProject.instance().mapLayersByName(layer_name)
        
        if layers:
            section_layer = layers[0]
            # Clear existing features if switching modes
            section_layer.dataProvider().truncate()
            # Force refresh of renderer when reusing layer
            section_layer.setRenderer(None)
        else:
            # Create new layer
            crs = QgsProject.instance().crs()
            section_layer = QgsVectorLayer(
                f"LineString?crs={crs.authid()}&field=id:integer&field=label:string&field=type:string&field=section_group:integer&field=dem_name:string&field=notes:string",
                layer_name,
                "memory"
            )
            QgsProject.instance().addMapLayer(section_layer)
        
        # Add features
        section_layer.startEditing()
        
        # Check if we have line data
        if 'line1' in self.profile_data:
            # Add line A-A'
            feature1 = QgsFeature()
            line1 = self.profile_data['line1']
            if isinstance(line1, QgsGeometry):
                feature1.setGeometry(line1)
            else:
                feature1.setGeometry(QgsGeometry.fromPolylineXY(line1))
            single_mode = self.profile_data.get('single_mode', False)
            feature1.setAttributes([
                self.section_count * 2 - 1,
                f"A{self.section_count}-A'{self.section_count}" if not single_mode else f"Section {self.section_count}",
                "Single" if single_mode else "Upper",
                self.section_count,  # section_group
                self.profile_data.get('dem1_name', 'DEM'),  # dem_name
                ""  # notes
            ])
            section_layer.addFeature(feature1)
        
        # Add line B-B' only if not in single mode
        single_mode = self.profile_data.get('single_mode', False)
        if not single_mode and 'line2' in self.profile_data and self.profile_data['line2'] is not None:
            feature2 = QgsFeature()
            feature2.setGeometry(QgsGeometry.fromPolylineXY(self.profile_data['line2']))
            feature2.setAttributes([
                self.section_count * 2,
                f"B{self.section_count}-B'{self.section_count}",
                "Lower",
                self.section_count,  # section_group
                self.profile_data.get('dem1_name', 'DEM'),  # dem_name
                ""  # notes
            ])
            section_layer.addFeature(feature2)
        
        section_layer.commitChanges()
        
        # Apply symbology based on mode
        if single_mode:
            self.setup_single_symbology(section_layer)
        else:
            self.setup_layer_symbology(section_layer)
        
        self.iface.mapCanvas().refresh()
        
        QtWidgets.QMessageBox.information(
            self,
            "Success",
            f"Section lines added to layer '{layer_name}'"
        )
    
    def create_multi_dem_layers(self):
        """Create separate layers for each DEM comparison"""
        # Primary DEM layer
        self.create_dem_section_layer(self.profile_data['dem1_name'], 
                                    self.profile_data['profile1'],
                                    self.profile_data['profile2'],
                                    is_primary=True)
        
        # First comparison DEM
        if self.profile_data.get('profile1_dem2'):
            self.create_dem_section_layer(self.profile_data['dem2_name'],
                                        self.profile_data['profile1_dem2'],
                                        self.profile_data['profile2_dem2'],
                                        is_primary=False)
        
        # Additional DEMs
        if 'additional_profiles' in self.profile_data:
            for dem_name, profiles in self.profile_data['additional_profiles'].items():
                self.create_dem_section_layer(dem_name,
                                            profiles['profile1'],
                                            profiles['profile2'],
                                            is_primary=False)
    
    def create_dem_section_layer(self, dem_name, profile1, profile2, is_primary=False):
        """Create section layer for a specific DEM"""
        # Clean DEM name for filename
        clean_name = dem_name.replace(' ', '_').replace('/', '_')
        layer_name = f"Sections_{clean_name}"
        
        # Create new layer
        crs = QgsProject.instance().crs()
        layer = QgsVectorLayer(
            f"LineString?crs={crs.authid()}&field=id:integer&field=label:string&field=type:string&field=dem_name:string&field=elevation_min:double&field=elevation_max:double",
            layer_name,
            "memory"
        )
        
        layer.startEditing()
        
        # Add profile A-A'
        feature1 = QgsFeature()
        
        # Handle different line formats
        line1 = self.profile_data['line1']
        if isinstance(line1, QgsGeometry):
            feature1.setGeometry(line1)
        else:
            feature1.setGeometry(QgsGeometry.fromPolylineXY(line1))
            
        feature1.setAttributes([
            self.section_count * 2 - 1,
            f"A{self.section_count}-A'{self.section_count}" if not self.profile_data.get('single_mode') else f"Section {self.section_count}",
            "Upper" if not self.profile_data.get('single_mode') else "Profile",
            dem_name,
            float(np.nanmin(profile1['elevations'])),
            float(np.nanmax(profile1['elevations']))
        ])
        layer.addFeature(feature1)
        
        # Add profile B-B' only if in dual mode
        if not self.profile_data.get('single_mode') and self.profile_data['line2'] is not None:
            feature2 = QgsFeature()
            
            # Handle different line formats
            line2 = self.profile_data['line2']
            if isinstance(line2, QgsGeometry):
                feature2.setGeometry(line2)
            else:
                feature2.setGeometry(QgsGeometry.fromPolylineXY(line2))
                
            feature2.setAttributes([
                self.section_count * 2,
                f"B{self.section_count}-B'{self.section_count}",
                "Lower",
                dem_name,
                float(np.nanmin(profile2['elevations'])),
                float(np.nanmax(profile2['elevations']))
            ])
            layer.addFeature(feature2)
        
        layer.commitChanges()
        
        # Apply symbology based on mode
        if self.profile_data.get('single_mode', False):
            self.setup_single_symbology(layer)
        else:
            self.setup_layer_symbology(layer)
        
        # Add to project
        QgsProject.instance().addMapLayer(layer)
        
        # Group layers if possible
        root = QgsProject.instance().layerTreeRoot()
        group_name = f"Profile_Sections_{self.section_count}"
        group = root.findGroup(group_name)
        if not group:
            group = root.insertGroup(0, group_name)
        
        # Move layer to group
        layer_node = root.findLayer(layer)
        if layer_node:
            clone = layer_node.clone()
            group.addChildNode(clone)
            parent = layer_node.parent()
            parent.removeChildNode(layer_node)
        
    def setup_single_symbology(self, layer):
        """Setup simple symbology for single section layer"""
        # Create simple symbol
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(QColor(255, 0, 0, 180))  # Red with alpha=180 (70% opacity)
        symbol.setWidth(2.0)
        
        # Create single symbol renderer
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        
        # Setup labeling
        settings = QgsPalLayerSettings()
        settings.fieldName = "label"
        settings.placement = QgsPalLayerSettings.Line
        
        text_format = QgsTextFormat()
        text_format.setSize(10)
        text_format.setColor(QColor(0, 0, 0))
        
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor(255, 255, 255))
        text_format.setBuffer(buffer_settings)
        
        settings.setFormat(text_format)
        
        labeling = QgsVectorLayerSimpleLabeling(settings)
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)
        
        layer.triggerRepaint()
    
    def setup_layer_symbology(self, layer):
        """Setup symbology for section layer"""
        # Create categorized renderer
        categories = []
        
        # Upper line style (red with transparency)
        symbol1 = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol1.setColor(QColor(255, 0, 0, 180))  # Red with alpha=180 (70% opacity)
        symbol1.setWidth(2.0)
        cat1 = QgsRendererCategory("Upper", symbol1, "Profile A-A'")
        categories.append(cat1)
        
        # Lower line style (blue with transparency)
        symbol2 = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol2.setColor(QColor(0, 0, 255, 180))  # Blue with alpha=180 (70% opacity)
        symbol2.setWidth(2.0)
        cat2 = QgsRendererCategory("Lower", symbol2, "Profile B-B'")
        categories.append(cat2)
        
        # Create renderer
        renderer = QgsCategorizedSymbolRenderer("type", categories)
        layer.setRenderer(renderer)
        
        # Setup labeling
        settings = QgsPalLayerSettings()
        settings.fieldName = "label"
        settings.placement = QgsPalLayerSettings.Line
        
        text_format = QgsTextFormat()
        text_format.setSize(10)
        text_format.setColor(QColor(0, 0, 0))
        
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor(255, 255, 255))
        text_format.setBuffer(buffer_settings)
        
        settings.setFormat(text_format)
        
        labeling = QgsVectorLayerSimpleLabeling(settings)
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)
        
        layer.triggerRepaint()
    
    def create_multi_section_layer(self):
        """Create layer for multi-section polygon data"""
        try:
            sections_data = self.profile_data.get('sections', [])
            if not sections_data:
                return
                
            # Create layer
            layer_name = f"Polygon_Sections_{len(sections_data)}_sides"
            crs = QgsProject.instance().crs()
            layer = QgsVectorLayer(
                f"LineString?crs={crs.authid()}&field=id:integer&field=name:string&field=side:integer&field=length:double&field=min_elev:double&field=max_elev:double",
                layer_name,
                "memory"
            )
            
            layer.startEditing()
            
            # Add each section
            for idx, section in enumerate(sections_data):
                feature = QgsFeature()
                feature.setGeometry(section['line_geometry'])
                feature.setAttributes([
                    idx + 1,
                    section['section_name'],
                    idx + 1,
                    float(section['total_distance']),
                    float(np.nanmin(section['elevations'])),
                    float(np.nanmax(section['elevations']))
                ])
                layer.addFeature(feature)
            
            layer.commitChanges()
            
            # Apply symbology
            self.setup_multi_section_symbology(layer)
            
            # Add to project
            QgsProject.instance().addMapLayer(layer)
            
            self.iface.messageBar().pushMessage(
                "Success", 
                f"Created polygon section layer with {len(sections_data)} sections",
                level=Qgis.Success,
                duration=3
            )
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error creating multi-section layer: {str(e)}", 
                                   'DualProfileViewer', Qgis.Critical)
            self.iface.messageBar().pushMessage(
                "Error",
                f"Failed to create section layer: {str(e)}",
                level=Qgis.Critical,
                duration=5
            )
    
    def setup_multi_section_symbology(self, layer):
        """Setup symbology for multi-section layer"""
        # Create categorized renderer by side
        categories = []
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'cyan']
        
        # Get unique sides
        unique_sides = set()
        for feature in layer.getFeatures():
            unique_sides.add(feature['side'])
        
        for side in sorted(unique_sides):
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol_layer = symbol.symbolLayer(0)
            symbol_layer.setColor(QColor(colors[(side - 1) % len(colors)]))
            symbol_layer.setWidth(2)
            
            category = QgsRendererCategory(side, symbol, f"Side {side}")
            categories.append(category)
        
        renderer = QgsCategorizedSymbolRenderer('side', categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        
    def export_csv(self):
        """Export profiles as CSV"""
        if not self.profile_data:
            return
            
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save profiles as CSV",
            f"profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                import csv
                
                # Check if this is multi-section data
                if self.profile_data.get('multi_section', False):
                    self.export_multi_section_csv(filename)
                    return
                
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    header = [
                        'Distance_m', 'X', 'Y',
                        'Elevation_A_m', 'Elevation_B_m',
                        'Difference_m', 'Offset_m'
                    ]
                    
                    # Add headers for comparison DEMs
                    if self.profile_data['profile1_dem2'] is not None:
                        header.extend([
                            f'Elevation_A_{self.profile_data["dem2_name"]}_m',
                            f'Elevation_B_{self.profile_data["dem2_name"]}_m'
                        ])
                    
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
                        
                        # Add comparison DEM data
                        if self.profile_data['profile1_dem2'] is not None:
                            row.extend([
                                self.profile_data['profile1_dem2']['elevations'][i],
                                self.profile_data['profile2_dem2']['elevations'][i]
                            ])
                        
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
            
            # Get output file
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save profile as vector",
                f"profile_vector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gpkg",
                "GeoPackage (*.gpkg);;Shapefile (*.shp)"
            )
            
            if filename:
                try:
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
                        f"Profile exported to:\n{filename}"
                    )
                    
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self, "Error",
                        f"Export error:\n{str(e)}"
                    )
                    
    def export_png(self):
        """Export plot as PNG"""
        if not self.profile_data:
            QtWidgets.QMessageBox.warning(self, "Warning", "No profile data to export")
            return
            
        # Get output file path
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Plot as Image",
            f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*.*)"
        )
        
        if not filename:
            return
            
        try:
            # Check if we're using matplotlib or plotly
            if self.use_web_action.isChecked() and PLOTLY_AVAILABLE:
                # Export from Plotly
                fig = self.create_plotly_figure()
                if fig:
                    # Try to use kaleido if available, otherwise use matplotlib
                    try:
                        fig.write_image(filename)
                        QtWidgets.QMessageBox.information(self, "Success", f"Plot exported to {filename}")
                    except Exception as e:
                        # Fall back to matplotlib
                        self.export_with_matplotlib(filename)
            else:
                # Export from matplotlib
                self.export_with_matplotlib(filename)
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to export image: {str(e)}")
    
    def export_with_matplotlib(self, filename):
        """Export using matplotlib"""
        if MATPLOTLIB_AVAILABLE and self.figure:
            # Ensure we have the latest plot
            self.plot_with_matplotlib()
            
            # Save figure
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
            QtWidgets.QMessageBox.information(self, "Success", f"Plot exported to {filename}")
        else:
            # Use the plot generator utility
            from .plot_generator import PlotGenerator
            success = PlotGenerator.generate_profile_plot(self.profile_data, filename)
            if success:
                QtWidgets.QMessageBox.information(self, "Success", f"Plot exported to {filename}")
            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "Failed to generate plot")
        
    def open_3d_viewer(self):
        """Open 3D viewer"""
        # Ask which viewer to use
        items = ['Geological Section View (PyVista)', 'Geological Section View (Plotly)']
        item, ok = QtWidgets.QInputDialog.getItem(self, "Select 3D View", 
                                                 "Choose visualization type:", 
                                                 items, 0, False)
        
        if ok and item:
            if item == 'Geological Section View (PyVista)':
                # PyVista geological view
                from .geological_3d_viewer import GeologicalSectionViewer
                geo_viewer = GeologicalSectionViewer(parent=self)
                
                # Check if we have multi-section data from polygon
                if hasattr(self, 'profile_data') and self.profile_data and self.profile_data.get('multi_section'):
                    # Pass multi-section data
                    geo_viewer.profile_data = self.profile_data
                    geo_viewer.handle_multi_section_data(self.profile_data)
                else:
                    # Pass all profile data including multi-DEM
                    if self.profile_data_list:
                        # Include additional profiles if available
                        all_profiles = self.profile_data_list.copy()
                        
                        # Add additional DEM profiles
                        if 'additional_profiles' in self.profile_data:
                            for dem_name, profiles in self.profile_data['additional_profiles'].items():
                                all_profiles.append(profiles['profile1'])
                                if profiles.get('profile2') is not None:
                                    all_profiles.append(profiles['profile2'])
                        
                        geo_viewer.load_sections(all_profiles)
                
                geo_viewer.show()
                geo_viewer.exec_()
        elif item == 'Geological Section View (Plotly)':
            # Plotly geological view
            try:
                from .plotly_geological_viewer import PlotlyGeologicalViewer
                plotly_viewer = PlotlyGeologicalViewer(parent=self)
                if self.profile_data:
                    plotly_viewer.set_profile_data(self.profile_data)
                plotly_viewer.exec_()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open Plotly viewer: {str(e)}")
            
    def show_help(self):
        """Show help"""
        QtWidgets.QMessageBox.information(
            self, "Help",
            "Dual Profile Viewer Help:\n\n"
            "1. Select a DEM/DTM from the dropdown\n"
            "2. Click 📏 Draw to start drawing\n"
            "3. Click on map to set start and end points\n"
            "4. Profiles are extracted automatically\n"
            "5. Use tabs to access different options\n"
            "6. Export in various formats\n\n"
            "For multi-DEM comparison:\n"
            "- Go to DEMs tab\n"
            "- Check 'Compare Multiple DEMs'\n"
            "- Select DEMs to compare"
        )
        
    def get_profile_data(self):
        """Get current profile data"""
        return self.profile_data
    
    def generate_layout(self):
        """Generate professional print layout"""
        if not self.profile_data and not self.all_sections:
            QtWidgets.QMessageBox.warning(self, "Warning", "No profile data to layout")
            return
            
        from .layout_generator import LayoutGenerator
        from .plot_generator import PlotGenerator
        
        # Check if this is multi-section polygon data
        if hasattr(self, 'profile_data') and self.profile_data and self.profile_data.get('multi_section'):
            # Handle multi-section layout
            from .multi_section_layout import MultiSectionLayoutGenerator
            
            # Generate multi-section plot
            plot_image = os.path.join(tempfile.gettempdir(), 'multi_section_plot.png')
            MultiSectionLayoutGenerator.generate_multi_section_plot(
                self.profile_data['sections'], 
                self.profile_data.get('dem1_name', 'DEM')
            )
            
            # Create layout with multi-section data
            generator = LayoutGenerator(self.iface)
            layout = generator.create_profile_layout(
                self.profile_data,
                plot_image_path=plot_image
            )
            
            if layout:
                # Open layout designer
                designer = self.iface.openLayoutDesigner(layout)
                QtWidgets.QMessageBox.information(self, "Layout Created", 
                    f"Multi-section layout created with {len(self.profile_data['sections'])} polygon sections")
            return
            
        # If we have stored sections, generate plots for all of them
        if self.all_sections:
            for section in self.all_sections:
                if not section.get('plot_image'):
                    try:
                        plot_image = os.path.join(tempfile.gettempdir(), 
                                                f'profile_plot_section_{section["section_number"]}.png')
                        PlotGenerator.generate_profile_plot(section['profile_data'], plot_image, dpi=300)
                        section['plot_image'] = plot_image
                    except Exception as e:
                        QgsMessageLog.logMessage(f"Plot generation failed for section {section['section_number']}: {str(e)}", 
                                               "DualProfileViewer", Qgis.Warning)
        
        # Use current profile for main display
        plot_image = None
        if self.profile_data:
            # Check if this is multi-section data
            if self.profile_data.get('multi_section'):
                # Generate multi-section plot
                try:
                    from .multi_section_handler import MultiSectionHandler
                    plot_image = os.path.join(tempfile.gettempdir(), 'multi_section_plot.png')
                    fig = MultiSectionHandler.create_matplotlib_multi_section(self.profile_data['sections'])
                    if fig:
                        fig.savefig(plot_image, dpi=300, bbox_inches='tight')
                        import matplotlib.pyplot as plt
                        plt.close(fig)
                except Exception as e:
                    QgsMessageLog.logMessage(f"Multi-section plot generation failed: {str(e)}", 
                                           "DualProfileViewer", Qgis.Warning)
            else:
                # Regular profile plot
                try:
                    plot_image = os.path.join(tempfile.gettempdir(), 'profile_plot_current.png')
                    PlotGenerator.generate_profile_plot(self.profile_data, plot_image, dpi=300)
                except Exception as e:
                    QgsMessageLog.logMessage(f"Current plot generation failed: {str(e)}", 
                                           "DualProfileViewer", Qgis.Warning)
        
        # Generate layout with all sections
        generator = LayoutGenerator(self.iface)
        
        # Check if we have AI report
        ai_report_text = getattr(self, 'last_ai_report', None)
        
        layout = generator.create_profile_layout(
            self.profile_data or (self.all_sections[0]['profile_data'] if self.all_sections else {}),
            plot_image_path=plot_image,
            all_sections=self.all_sections if len(self.all_sections) > 0 else None,
            ai_report_text=ai_report_text
        )
        
        if layout:
            # Open layout designer
            designer = self.iface.openLayoutDesigner(layout)
            QtWidgets.QMessageBox.information(self, "Layout Created", 
                f"Layout created with {len(self.all_sections)} section(s) across {max(1, len(self.all_sections))} page(s)")
            
            msg = "Professional layout created and opened in Layout Designer."
            if not plot_image:
                msg += "\n\nNote: Profile plots could not be generated. You can add them manually in the layout designer."
            
            QtWidgets.QMessageBox.information(self, "Layout Created", msg)
    
    def toggle_plot_mode(self, checked):
        """Toggle between web view and matplotlib"""
        if checked and self.web_view:
            self.plot_stack.setCurrentWidget(self.web_view)
        else:
            self.plot_stack.setCurrentWidget(self.canvas)
        
        # Refresh plot if we have data
        if self.profile_data:
            self.plot_profiles()
    
    def generate_plot_image_for_section(self, section_data):
        """Generate plot image for a section using matplotlib"""
        try:
            from .plot_generator import PlotGenerator
            import tempfile
            import os
            
            # Create temp file for plot
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_path = temp_file.name
            temp_file.close()
            
            # Generate plot
            if PlotGenerator.generate_profile_plot(section_data['profile_data'], temp_path):
                section_data['plot_image'] = temp_path
        except Exception as e:
            QgsMessageLog.logMessage(f"Failed to generate plot image: {str(e)}", 
                                   "DualProfileViewer", Qgis.Warning)
    
    def open_in_browser(self):
        """Open plot in external browser"""
        if not self.profile_data:
            QtWidgets.QMessageBox.warning(self, "Warning", "No profile data to display")
            return
            
        if not PLOTLY_AVAILABLE:
            QtWidgets.QMessageBox.warning(self, "Warning", "Plotly is not installed. Install with: pip install plotly")
            return
            
        try:
            # Generate plot
            fig = self.create_plotly_figure()
            
            # Save to temporary file and open
            import tempfile
            import webbrowser
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                fig.write_html(f.name, include_plotlyjs='cdn')
                temp_path = f.name
                
            # Open in browser
            webbrowser.open('file://' + temp_path)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open in browser: {str(e)}")
        
    def extract_polygon_profiles(self):
        """Extract profiles for all polygon sections"""
        try:
            from .multi_section_handler import MultiSectionHandler
            
            dem_layer_id = self.combo_dem.currentData()
            if not dem_layer_id:
                return
                
            dem_layer = QgsProject.instance().mapLayer(dem_layer_id)
            if not dem_layer:
                return
                
            num_samples = self.spin_samples.value()
            
            # Process all sections
            self.multi_sections_data = MultiSectionHandler.process_polygon_sections(
                self.polygon_data_full, dem_layer, self.multi_dem_widget, num_samples
            )
            
            # Store for visualization
            self.profile_data = {
                'multi_section': True,
                'sections': self.multi_sections_data,
                'dem1_name': dem_layer.name(),
                'polygon': self.polygon_data_full['polygon'],
                'section_count': len(self.multi_sections_data)
            }
            
            # Visualize
            self.plot_multi_section_profiles()
            
            # Update statistics
            self.update_multi_section_statistics()
            
            # Enable export buttons
            self.enable_export_buttons(True)
            
            # Enable 3D viewer
            self.view3d_action.setEnabled(True)
            
            # Enable layout generator
            self.layout_action.setEnabled(True)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to extract polygon profiles: {str(e)}")
            
    def plot_multi_section_profiles(self):
        """Plot multiple section profiles"""
        try:
            from .multi_section_handler import MultiSectionHandler
            
            # Enable browser button
            self.open_browser_action.setEnabled(True)
            
            # Check which view is active
            if self.use_web_action.isChecked() and PLOTLY_AVAILABLE:
                # Use Plotly
                fig = MultiSectionHandler.create_multi_section_plots(
                    self.multi_sections_data, use_plotly=True
                )
                if fig:
                    # Display in web view
                    html = fig.to_html(include_plotlyjs='cdn')
                    if self.web_view:
                        self.web_view.setHtml(html)
            else:
                # Use matplotlib
                if MATPLOTLIB_AVAILABLE and self.figure:
                    self.figure.clear()
                    fig = MultiSectionHandler.create_matplotlib_multi_section(
                        self.multi_sections_data
                    )
                    if fig:
                        self.canvas.draw()
                        
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Plot Error", f"Failed to create plots: {str(e)}")
            
    def update_multi_section_statistics(self):
        """Update statistics for multiple sections"""
        try:
            from .multi_section_handler import MultiSectionHandler
            
            stats = MultiSectionHandler.calculate_multi_section_statistics(
                self.multi_sections_data
            )
            
            stats_text = MultiSectionHandler.format_statistics_text(stats)
            
            # Update info text
            self.info_text.setPlainText(stats_text)
            
            # Store stats for layout
            self.section_statistics = stats
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Stats Error", f"Failed to calculate statistics: {str(e)}")
    
    def export_multi_section_csv(self, filename):
        """Export multi-section data to CSV"""
        try:
            import csv
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write metadata
                writer.writerow(['# Multi-Section Profile Data'])
                writer.writerow(['# DEM:', self.profile_data.get('dem1_name', 'Unknown')])
                writer.writerow(['# Sections:', len(self.multi_sections_data)])
                writer.writerow([])
                
                # Write each section
                for idx, section in enumerate(self.multi_sections_data):
                    writer.writerow([f'# Section {idx + 1}: {section["section_name"]}'])
                    writer.writerow(['Distance_m', 'Elevation_m', 'X', 'Y'])
                    
                    # Write data points
                    for i in range(len(section['distances'])):
                        # Calculate X, Y positions
                        ratio = section['distances'][i] / section['total_distance'] if section['total_distance'] > 0 else 0
                        x = section['start'].x() + ratio * (section['end'].x() - section['start'].x())
                        y = section['start'].y() + ratio * (section['end'].y() - section['start'].y())
                        
                        writer.writerow([
                            f"{section['distances'][i]:.2f}",
                            f"{section['elevations'][i]:.3f}",
                            f"{x:.6f}",
                            f"{y:.6f}"
                        ])
                    
                    writer.writerow([])  # Empty row between sections
                
            QtWidgets.QMessageBox.information(self, "Success", f"Multi-section data exported to {filename}")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Error", f"Failed to export CSV: {str(e)}")
    
    def get_all_profile_data(self):
        """Get all profile data for 3D viewer"""
        return self.profile_data_list
    
    def on_offset_changed(self, value):
        """Handle offset distance change"""
        # Update the current drawing tool if active
        if hasattr(self, 'map_tool') and self.map_tool and hasattr(self.map_tool, 'offset_distance'):
            self.map_tool.offset_distance = value
        if hasattr(self, 'current_tool') and self.current_tool and hasattr(self.current_tool, 'offset_distance'):
            self.current_tool.offset_distance = value
    
    def generate_ai_report(self):
        """Open AI report generator"""
        try:
            from .ai_report_generator import AIReportGenerator
            
            if not self.profile_data and not self.all_sections:
                QtWidgets.QMessageBox.warning(self, "Warning", "No profile data available for report generation")
                return
                
            # Prepare data for AI report - include all sections if available
            report_data = {}
            if self.all_sections:
                # Include all sections data
                report_data['all_sections'] = self.all_sections
                report_data['section_count'] = len(self.all_sections)
                # Include current profile data if available
                if self.profile_data:
                    report_data.update(self.profile_data)
                else:
                    # Use first section data as base
                    report_data.update(self.all_sections[0]['profile_data'])
            else:
                # Use current profile data
                report_data = self.profile_data
                
            # Open AI report dialog
            ai_dialog = AIReportGenerator(report_data, parent=self)
            if ai_dialog.exec_():
                # Store the generated report
                self.last_ai_report = ai_dialog.get_report_text()
            else:
                self.last_ai_report = None
            
        except ImportError:
            QtWidgets.QMessageBox.information(self, "AI Report Generator", 
                "AI Report Generator requires additional dependencies.\n\n"
                "To use this feature, install:\n"
                "- requests: pip install requests\n\n"
                "For full functionality, you'll also need an API key from:\n"
                "- OpenAI (GPT-4): https://openai.com/api/\n"
                "- Anthropic (Claude): https://www.anthropic.com/api/"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open AI report generator: {str(e)}")