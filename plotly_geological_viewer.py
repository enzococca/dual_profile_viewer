# -*- coding: utf-8 -*-
"""
Plotly Geological/Stratigraphic 3D Viewer
Interactive 3D visualization of geological sections using Plotly
"""

import numpy as np
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                QPushButton, QCheckBox, QLabel,
                                QSlider, QComboBox, QGroupBox,
                                QFormLayout, QListWidget,
                                QListWidgetItem, QMessageBox)
from qgis.core import QgsProject, QgsVectorLayer, Qgis, QgsMessageLog
import tempfile
import webbrowser

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

class PlotlyGeologicalViewer(QDialog):
    """Interactive 3D geological section viewer using Plotly"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plotly Geological Section Viewer")
        self.resize(800, 600)
        
        # Data storage
        self.profile_data = None
        self.sections = []
        self.section_layers = []  # Layers from QGIS TOC
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        layout = QVBoxLayout()
        
        if not PLOTLY_AVAILABLE:
            label = QLabel("Plotly not available. Install with: pip install plotly")
            layout.addWidget(label)
            self.setLayout(layout)
            return
        
        # Controls
        controls_group = QGroupBox("Visualization Controls")
        controls_layout = QFormLayout()
        
        # Section source
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Current Profile", "Section Layers from Project"])
        self.source_combo.currentTextChanged.connect(self.on_source_changed)
        controls_layout.addRow("Data Source:", self.source_combo)
        
        # Section layer list (initially hidden)
        self.layer_list = QListWidget()
        self.layer_list.setSelectionMode(QListWidget.MultiSelection)
        self.layer_list.setMaximumHeight(150)
        self.load_section_layers()
        controls_layout.addRow("Select Sections:", self.layer_list)
        self.layer_list.setVisible(False)
        
        # Visualization options
        self.show_walls_cb = QCheckBox("Show as 3D Walls")
        self.show_walls_cb.setChecked(True)
        controls_layout.addRow(self.show_walls_cb)
        
        self.show_layers_cb = QCheckBox("Show Stratigraphic Layers")
        self.show_layers_cb.setChecked(True)
        controls_layout.addRow(self.show_layers_cb)
        
        self.show_intersections_cb = QCheckBox("Highlight Intersections")
        self.show_intersections_cb.setChecked(True)
        controls_layout.addRow(self.show_intersections_cb)
        
        # Wall thickness
        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setRange(1, 50)
        self.thickness_slider.setValue(10)
        self.thickness_label = QLabel("10 m")
        self.thickness_slider.valueChanged.connect(
            lambda v: self.thickness_label.setText(f"{v} m"))
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(self.thickness_slider)
        thickness_layout.addWidget(self.thickness_label)
        controls_layout.addRow("Wall Thickness:", thickness_layout)
        
        # Vertical exaggeration
        self.exag_slider = QSlider(Qt.Horizontal)
        self.exag_slider.setRange(1, 50)
        self.exag_slider.setValue(10)
        self.exag_label = QLabel("1.0x")
        self.exag_slider.valueChanged.connect(
            lambda v: self.exag_label.setText(f"{v/10:.1f}x"))
        exag_layout = QHBoxLayout()
        exag_layout.addWidget(self.exag_slider)
        exag_layout.addWidget(self.exag_label)
        controls_layout.addRow("Vertical Scale:", exag_layout)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("Create 3D Visualization")
        self.create_btn.clicked.connect(self.create_visualization)
        button_layout.addWidget(self.create_btn)
        
        self.export_btn = QPushButton("Export HTML")
        self.export_btn.clicked.connect(self.export_html)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
        
        # Info label
        self.info_label = QLabel("Click 'Create 3D Visualization' to generate the geological view")
        layout.addWidget(self.info_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def load_section_layers(self):
        """Load section layers from QGIS project"""
        self.layer_list.clear()
        
        # Look for vector layers that might contain sections
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 1:  # Line geometry
                # Check if it might be a section layer
                if any(keyword in layer.name().lower() for keyword in ['section', 'profile', 'sezione']):
                    item = QListWidgetItem(layer.name())
                    item.setData(Qt.UserRole, layer.id())
                    self.layer_list.addItem(item)
                    
    def on_source_changed(self, source):
        """Handle source selection change"""
        if source == "Section Layers from Project":
            self.layer_list.setVisible(True)
        else:
            self.layer_list.setVisible(False)
            
    def set_profile_data(self, profile_data):
        """Set profile data from the main viewer"""
        self.profile_data = profile_data
        
    def create_visualization(self):
        """Create the 3D geological visualization"""
        try:
            if self.source_combo.currentText() == "Current Profile":
                if not self.profile_data:
                    QMessageBox.warning(self, "Warning", "No profile data available")
                    return
                self.create_from_current_profile()
            else:
                self.create_from_layers()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create visualization: {str(e)}")
            
    def create_from_current_profile(self):
        """Create visualization from current profile data"""
        fig = go.Figure()
        
        # Get settings
        thickness = self.thickness_slider.value()
        exag = self.exag_slider.value() / 10.0
        
        if self.show_walls_cb.isChecked():
            # Create 3D walls
            self.add_wall_to_figure(fig, self.profile_data, thickness, exag)
        else:
            # Create simple 3D lines
            self.add_lines_to_figure(fig, self.profile_data, exag)
            
        # Configure layout
        fig.update_layout(
            title="Geological Section 3D View",
            scene=dict(
                xaxis_title="X (m)",
                yaxis_title="Y (m)",
                zaxis_title="Elevation (m)",
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=exag/2)
            ),
            showlegend=True,
            height=800
        )
        
        # Open in browser
        self.open_in_browser(fig)
        self.export_btn.setEnabled(True)
        self.current_fig = fig
        
    def create_from_layers(self):
        """Create visualization from selected layers"""
        selected_items = self.layer_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "No sections selected")
            return
            
        fig = go.Figure()
        
        # Process each selected layer
        for item in selected_items:
            layer_id = item.data(Qt.UserRole)
            layer = QgsProject.instance().mapLayer(layer_id)
            if layer:
                self.process_section_layer(fig, layer)
                
        # Configure layout
        fig.update_layout(
            title="Multiple Geological Sections",
            scene=dict(
                xaxis_title="X (m)",
                yaxis_title="Y (m)",
                zaxis_title="Elevation (m)",
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.5)
            ),
            showlegend=True,
            height=800
        )
        
        # Open in browser
        self.open_in_browser(fig)
        self.export_btn.setEnabled(True)
        self.current_fig = fig
        
    def add_wall_to_figure(self, fig, profile_data, thickness, exag):
        """Add a 3D wall to the figure"""
        # Extract profile lines
        if 'line1' in profile_data and 'line2' in profile_data:
            line1 = profile_data['line1']
            line2 = profile_data['line2']
            
            # Get elevations
            profile1 = profile_data['profile1']
            profile2 = profile_data['profile2']
            
            # Create wall vertices
            x1 = [pt.x() for pt in line1]
            y1 = [pt.y() for pt in line1]
            z1 = np.array(profile1['elevations']) * exag
            
            x2 = [pt.x() for pt in line2]
            y2 = [pt.y() for pt in line2]
            z2 = np.array(profile2['elevations']) * exag
            
            # Create mesh3d for the wall
            vertices_x = x1 + x2
            vertices_y = y1 + y2
            vertices_z = list(z1) + list(z2)
            
            # Create faces
            n = len(x1)
            faces_i = []
            faces_j = []
            faces_k = []
            
            for i in range(n-1):
                # Upper triangle
                faces_i.extend([i, i, i+1])
                faces_j.extend([i+n, i+1, i+1+n])
                faces_k.extend([i+1, i+1+n, i+n])
                
            # Add primary DEM wall
            fig.add_trace(go.Mesh3d(
                x=vertices_x,
                y=vertices_y,
                z=vertices_z,
                i=faces_i,
                j=faces_j,
                k=faces_k,
                color='brown',
                opacity=0.7,
                name=profile_data.get('dem1_name', 'Primary DEM')
            ))
            
            # Add comparison DEMs as different colored layers
            if self.show_layers_cb.isChecked() and 'profile1_dem2' in profile_data:
                self.add_comparison_layers(fig, profile_data, line1, line2, exag)
                
            # Add intersection markers if multiple walls
            if self.show_intersections_cb.isChecked():
                self.add_intersection_markers(fig, profile_data)
                
    def add_comparison_layers(self, fig, profile_data, line1, line2, exag):
        """Add comparison DEM layers with different colors"""
        colors = ['orange', 'green', 'purple', 'red', 'blue']
        color_idx = 0
        
        # Add first comparison DEM
        if profile_data['profile1_dem2'] is not None:
            x1 = [pt.x() for pt in line1]
            y1 = [pt.y() for pt in line1]
            z1 = np.array(profile_data['profile1_dem2']['elevations']) * exag
            
            x2 = [pt.x() for pt in line2]
            y2 = [pt.y() for pt in line2]
            z2 = np.array(profile_data['profile2_dem2']['elevations']) * exag
            
            # Create mesh
            vertices_x = x1 + x2
            vertices_y = y1 + y2
            vertices_z = list(z1) + list(z2)
            
            n = len(x1)
            faces_i = []
            faces_j = []
            faces_k = []
            
            for i in range(n-1):
                faces_i.extend([i, i, i+1])
                faces_j.extend([i+n, i+1, i+1+n])
                faces_k.extend([i+1, i+1+n, i+n])
                
            fig.add_trace(go.Mesh3d(
                x=vertices_x,
                y=vertices_y,
                z=vertices_z,
                i=faces_i,
                j=faces_j,
                k=faces_k,
                color=colors[color_idx % len(colors)],
                opacity=0.6,
                name=profile_data.get('dem2_name', 'Comparison DEM')
            ))
            color_idx += 1
            
        # Add additional DEMs
        if 'additional_profiles' in profile_data:
            for dem_name, profiles in profile_data['additional_profiles'].items():
                x1 = [pt.x() for pt in line1]
                y1 = [pt.y() for pt in line1]
                z1 = np.array(profiles['profile1']['elevations']) * exag
                
                x2 = [pt.x() for pt in line2]
                y2 = [pt.y() for pt in line2]
                z2 = np.array(profiles['profile2']['elevations']) * exag
                
                vertices_x = x1 + x2
                vertices_y = y1 + y2
                vertices_z = list(z1) + list(z2)
                
                n = len(x1)
                faces_i = []
                faces_j = []
                faces_k = []
                
                for i in range(n-1):
                    faces_i.extend([i, i, i+1])
                    faces_j.extend([i+n, i+1, i+1+n])
                    faces_k.extend([i+1, i+1+n, i+n])
                    
                fig.add_trace(go.Mesh3d(
                    x=vertices_x,
                    y=vertices_y,
                    z=vertices_z,
                    i=faces_i,
                    j=faces_j,
                    k=faces_k,
                    color=colors[color_idx % len(colors)],
                    opacity=0.5,
                    name=dem_name
                ))
                color_idx += 1
                
    def add_lines_to_figure(self, fig, profile_data, exag):
        """Add simple 3D lines to the figure"""
        # Add profile lines
        if 'line1' in profile_data:
            line1 = profile_data['line1']
            profile1 = profile_data['profile1']
            
            x = [pt.x() for pt in line1]
            y = [pt.y() for pt in line1]
            z = np.array(profile1['elevations']) * exag
            
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines+markers',
                name=f"Profile A-A' ({profile_data.get('dem1_name', 'DEM')})",
                line=dict(color='red', width=4),
                marker=dict(size=3)
            ))
            
        if 'line2' in profile_data:
            line2 = profile_data['line2']
            profile2 = profile_data['profile2']
            
            x = [pt.x() for pt in line2]
            y = [pt.y() for pt in line2]
            z = np.array(profile2['elevations']) * exag
            
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines+markers',
                name=f"Profile B-B' ({profile_data.get('dem1_name', 'DEM')})",
                line=dict(color='blue', width=4),
                marker=dict(size=3)
            ))
            
    def process_section_layer(self, fig, layer):
        """Process a section layer from QGIS"""
        # This would extract the geometry and attributes from the layer
        # and create 3D walls or lines based on the features
        features = layer.getFeatures()
        
        for feature in features:
            geom = feature.geometry()
            if geom:
                # Extract points
                points = []
                if geom.isMultipart():
                    for part in geom.asMultiPolyline():
                        points.extend(part)
                else:
                    points = geom.asPolyline()
                    
                if points:
                    x = [pt.x() for pt in points]
                    y = [pt.y() for pt in points]
                    # For demo, use a default elevation profile
                    z = [100] * len(points)  # Would need actual elevation data
                    
                    fig.add_trace(go.Scatter3d(
                        x=x, y=y, z=z,
                        mode='lines',
                        name=f"{layer.name()} - Feature {feature.id()}",
                        line=dict(width=4)
                    ))
                    
    def add_intersection_markers(self, fig, profile_data):
        """Add markers at wall intersections"""
        # This would calculate actual intersections
        # For now, just a placeholder
        pass
        
    def open_in_browser(self, fig):
        """Open the figure in web browser"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            fig.write_html(f.name, include_plotlyjs='cdn')
            webbrowser.open('file://' + f.name)
            self.info_label.setText(f"Visualization opened in browser: {f.name}")
            
    def export_html(self):
        """Export the visualization as HTML"""
        if hasattr(self, 'current_fig'):
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export HTML",
                "geological_section.html",
                "HTML Files (*.html)"
            )
            if filename:
                self.current_fig.write_html(filename, include_plotlyjs='cdn')
                QMessageBox.information(self, "Success", f"Exported to {filename}")