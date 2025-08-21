# -*- coding: utf-8 -*-
"""
Advanced 3D Profile Viewer with PyVistaQt
Real-scale sections with intersections, texturing, and interactivity
"""

import numpy as np
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QGroupBox, QSlider, QLabel, QComboBox, QCheckBox,
                             QSpinBox, QDoubleSpinBox, QColorDialog, QTableWidget,
                             QTableWidgetItem, QSplitter, QWidget, QFileDialog,
                             QMessageBox, QToolBar, QAction, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QColor
from qgis.core import (QgsProject, QgsCoordinateTransform, QgsCoordinateReferenceSystem,
                      QgsPointXY, QgsGeometry, QgsFeature, QgsVectorLayer,
                      QgsField, QgsFields, QgsWkbTypes, QgsMessageLog, Qgis)
from qgis.PyQt.QtCore import QVariant
import json
import os

try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    QgsMessageLog.logMessage("PyVista not available. Install with: pip install pyvista pyvistaqt", 
                            "DualProfileViewer", Qgis.Warning)

class Advanced3DViewer(QDialog):
    """Advanced 3D visualization widget for profile sections"""
    
    metadata_updated = pyqtSignal(dict)
    point_selected = pyqtSignal(tuple)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced 3D Profile Viewer")
        self.resize(1200, 800)
        
        # Data storage
        self.profiles = []  # List of profile data dicts
        self.meshes = []    # PyVista meshes
        self.actors = []    # Rendered actors
        self.metadata = {}  # Metadata for points/sections
        self.intersection_points = []
        
        # Settings
        self.section_colors = {
            'primary': (1.0, 0.0, 0.0),    # Red
            'secondary': (0.0, 0.0, 1.0),   # Blue
            'intersection': (1.0, 1.0, 0.0)  # Yellow
        }
        
        self.scale_factor = 1.0  # Real-world scale
        self.vertical_exaggeration = 1.0
        
        if PYVISTA_AVAILABLE:
            self.init_ui()
        else:
            self.show_installation_message()
    
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout()
        
        # Create toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Create splitter for 3D view and controls
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - 3D viewer
        viewer_widget = QWidget()
        viewer_layout = QVBoxLayout()
        
        # Initialize PyVista plotter
        self.plotter = QtInteractor(viewer_widget)
        viewer_layout.addWidget(self.plotter.interactor)
        viewer_widget.setLayout(viewer_layout)
        
        # Right side - Controls
        controls_widget = self.create_controls()
        
        splitter.addWidget(viewer_widget)
        splitter.addWidget(controls_widget)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        
        # Bottom - Metadata table
        self.metadata_table = self.create_metadata_table()
        main_layout.addWidget(self.metadata_table)
        
        self.setLayout(main_layout)
        
        # Setup plotter
        self.setup_plotter()
        
    def create_toolbar(self):
        """Create toolbar with main actions"""
        toolbar = QToolBar()
        
        # Load profiles action
        load_action = QAction("Load Profiles", self)
        load_action.triggered.connect(self.load_profiles)
        toolbar.addAction(load_action)
        
        # Add plane action
        plane_action = QAction("Add Reference Plane", self)
        plane_action.triggered.connect(self.add_reference_plane)
        toolbar.addAction(plane_action)
        
        # Export action
        export_action = QAction("Export 3D", self)
        export_action.triggered.connect(self.export_3d)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # View presets
        view_menu = QMenu("View Presets", self)
        view_menu.addAction("Top View", lambda: self.set_view('top'))
        view_menu.addAction("Front View", lambda: self.set_view('front'))
        view_menu.addAction("Side View", lambda: self.set_view('side'))
        view_menu.addAction("Isometric", lambda: self.set_view('isometric'))
        
        view_button = QPushButton("View Presets")
        view_button.setMenu(view_menu)
        toolbar.addWidget(view_button)
        
        return toolbar
    
    def create_controls(self):
        """Create control panel"""
        controls = QWidget()
        layout = QVBoxLayout()
        
        # Display options
        display_group = QGroupBox("Display Options")
        display_layout = QVBoxLayout()
        
        # Vertical exaggeration
        exag_layout = QHBoxLayout()
        exag_layout.addWidget(QLabel("Vertical Exaggeration:"))
        self.exag_slider = QSlider(Qt.Horizontal)
        self.exag_slider.setRange(10, 500)
        self.exag_slider.setValue(100)
        self.exag_slider.valueChanged.connect(self.update_vertical_exaggeration)
        self.exag_label = QLabel("1.0x")
        exag_layout.addWidget(self.exag_slider)
        exag_layout.addWidget(self.exag_label)
        display_layout.addLayout(exag_layout)
        
        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        opacity_layout.addWidget(self.opacity_slider)
        display_layout.addLayout(opacity_layout)
        
        # Show options
        self.show_edges_cb = QCheckBox("Show Edges")
        self.show_edges_cb.setChecked(True)
        self.show_edges_cb.stateChanged.connect(self.update_display)
        display_layout.addWidget(self.show_edges_cb)
        
        self.show_intersections_cb = QCheckBox("Show Intersections")
        self.show_intersections_cb.setChecked(True)
        self.show_intersections_cb.stateChanged.connect(self.update_display)
        display_layout.addWidget(self.show_intersections_cb)
        
        self.show_grid_cb = QCheckBox("Show Grid")
        self.show_grid_cb.setChecked(True)
        self.show_grid_cb.stateChanged.connect(self.toggle_grid)
        display_layout.addWidget(self.show_grid_cb)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Texture options
        texture_group = QGroupBox("Texture Options")
        texture_layout = QVBoxLayout()
        
        # Texture type
        tex_type_layout = QHBoxLayout()
        tex_type_layout.addWidget(QLabel("Texture:"))
        self.texture_combo = QComboBox()
        self.texture_combo.addItems(["Solid Color", "Elevation Gradient", 
                                    "Slope Gradient", "Custom Texture"])
        self.texture_combo.currentIndexChanged.connect(self.update_texture)
        tex_type_layout.addWidget(self.texture_combo)
        texture_layout.addLayout(tex_type_layout)
        
        # Color pickers
        color_layout = QHBoxLayout()
        self.color1_btn = QPushButton("Primary Color")
        self.color1_btn.clicked.connect(lambda: self.pick_color('primary'))
        self.color2_btn = QPushButton("Secondary Color")
        self.color2_btn.clicked.connect(lambda: self.pick_color('secondary'))
        color_layout.addWidget(self.color1_btn)
        color_layout.addWidget(self.color2_btn)
        texture_layout.addLayout(color_layout)
        
        texture_group.setLayout(texture_layout)
        layout.addWidget(texture_group)
        
        # Section properties
        section_group = QGroupBox("Section Properties")
        section_layout = QVBoxLayout()
        
        # Section selection
        self.section_combo = QComboBox()
        self.section_combo.currentIndexChanged.connect(self.select_section)
        section_layout.addWidget(QLabel("Select Section:"))
        section_layout.addWidget(self.section_combo)
        
        # Section scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale:"))
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 10.0)
        self.scale_spin.setValue(1.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.valueChanged.connect(self.update_section_scale)
        scale_layout.addWidget(self.scale_spin)
        section_layout.addLayout(scale_layout)
        
        section_group.setLayout(section_layout)
        layout.addWidget(section_group)
        
        # Intersection tools
        intersect_group = QGroupBox("Intersection Analysis")
        intersect_layout = QVBoxLayout()
        
        self.auto_intersect_btn = QPushButton("Calculate Intersections")
        self.auto_intersect_btn.clicked.connect(self.calculate_intersections)
        intersect_layout.addWidget(self.auto_intersect_btn)
        
        self.intersect_info = QLabel("No intersections calculated")
        intersect_layout.addWidget(self.intersect_info)
        
        intersect_group.setLayout(intersect_layout)
        layout.addWidget(intersect_group)
        
        layout.addStretch()
        controls.setLayout(layout)
        return controls
    
    def create_metadata_table(self):
        """Create metadata table widget"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Point ID", "X", "Y", "Z", "Notes"])
        table.setMaximumHeight(150)
        return table
    
    def setup_plotter(self):
        """Setup the PyVista plotter"""
        self.plotter.set_background('white')
        self.plotter.show_axes()
        self.plotter.show_grid()
        
        # Enable picking
        self.plotter.enable_point_picking(callback=self.on_point_picked, 
                                         show_message=True,
                                         color='yellow',
                                         point_size=10)
        
        # Add camera controls
        self.plotter.camera.zoom(1.2)
    
    def load_profiles(self, profile_data_list=None):
        """Load profile data into 3D viewer"""
        if profile_data_list is None:
            # Get from current QGIS project if not provided
            profile_data_list = self.get_profiles_from_project()
        
        # Ensure profile_data_list is a list
        if not isinstance(profile_data_list, list):
            QgsMessageLog.logMessage("Invalid profile data received, expected list", 
                                   "DualProfileViewer", Qgis.Warning)
            profile_data_list = []
        
        self.profiles = profile_data_list
        self.update_section_combo()
        
        # Only create 3D sections if we have profiles
        if self.profiles:
            self.create_3d_sections()
            self.plotter.reset_camera()
    
    def create_3d_sections(self):
        """Create 3D mesh sections from profile data"""
        self.plotter.clear()
        self.meshes.clear()
        self.actors.clear()
        
        for i, profile in enumerate(self.profiles):
            if 'distances' in profile and 'elevations' in profile:
                # Create section mesh
                mesh = self.create_section_mesh(profile, i)
                if mesh:
                    self.meshes.append(mesh)
                    
                    # Determine color
                    if i == 0:
                        color = self.section_colors['primary']
                    elif i == 1:
                        color = self.section_colors['secondary']
                    else:
                        color = (0.5, 0.5, 0.5)  # Gray for additional sections
                    
                    # Add to plotter
                    actor = self.plotter.add_mesh(mesh, 
                                                 color=color,
                                                 opacity=self.opacity_slider.value()/100,
                                                 show_edges=self.show_edges_cb.isChecked(),
                                                 label=f"Section_{i}")
                    self.actors.append(actor)
        
        # Calculate and show intersections if requested
        if self.show_intersections_cb.isChecked() and len(self.meshes) > 1:
            self.calculate_intersections()
    
    def create_section_mesh(self, profile_data, section_index):
        """Create a 3D mesh from profile data"""
        try:
            distances = np.array(profile_data['distances'])
            elevations = np.array(profile_data['elevations']) * self.vertical_exaggeration
            
            # Get real-world coordinates if available
            if 'coordinates' in profile_data:
                coords = profile_data['coordinates']
                x_coords = np.array([c[0] for c in coords])
                y_coords = np.array([c[1] for c in coords])
            else:
                # Create synthetic coordinates based on section index
                angle = section_index * np.pi / 4  # 45 degree separation
                x_coords = distances * np.cos(angle)
                y_coords = distances * np.sin(angle)
            
            # Create surface mesh with thickness
            thickness = 10 * self.scale_factor  # Section thickness
            
            # Create points for top and bottom of section
            n_points = len(distances)
            points = []
            
            # Top surface
            for i in range(n_points):
                points.append([x_coords[i], y_coords[i], elevations[i]])
            
            # Bottom surface (flat or following terrain)
            min_elev = np.min(elevations) - thickness
            for i in range(n_points):
                points.append([x_coords[i], y_coords[i], min_elev])
            
            points = np.array(points)
            
            # Create faces (quads connecting top and bottom)
            faces = []
            for i in range(n_points - 1):
                # Create quad face
                face = [4,  # Number of points in face
                       i, i+1, i+1+n_points, i+n_points]
                faces.extend(face)
            
            # Create mesh
            mesh = pv.PolyData(points, faces)
            
            # Add data arrays for coloring
            mesh["Elevation"] = points[:, 2]
            
            # Calculate slope if needed
            if self.texture_combo.currentText() == "Slope Gradient":
                gradients = np.gradient(elevations)
                slopes = np.abs(gradients)
                # Extend slopes for both surfaces
                mesh["Slope"] = np.concatenate([slopes, slopes])
            
            return mesh
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error creating section mesh: {str(e)}", 
                                   "DualProfileViewer", Qgis.Warning)
            return None
    
    def calculate_intersections(self):
        """Calculate intersection points between sections"""
        if len(self.meshes) < 2:
            return
        
        self.intersection_points.clear()
        
        try:
            # Calculate intersections between first two sections
            mesh1 = self.meshes[0]
            mesh2 = self.meshes[1]
            
            # Use VTK intersection filter
            intersection = mesh1.intersection(mesh2)
            
            # Check if intersection has points
            if intersection is not None and len(intersection.points) > 0:
                # Add intersection line to plotter
                self.plotter.add_mesh(intersection, 
                                    color=self.section_colors['intersection'],
                                    line_width=3,
                                    label="Intersection")
                
                # Store intersection points
                self.intersection_points = intersection.points
                
                # Update info
                n_points = len(intersection.points)
                self.intersect_info.setText(f"Found {n_points} intersection points")
                
                # Add markers at intersection points
                for point in intersection.points[:10]:  # Limit to first 10 points
                    self.plotter.add_mesh(pv.Sphere(radius=5, center=point),
                                        color='yellow',
                                        opacity=0.8)
        except Exception as e:
            QgsMessageLog.logMessage(f"Error calculating intersections: {str(e)}", 
                                   "DualProfileViewer", Qgis.Warning)
    
    def add_reference_plane(self):
        """Add a reference plane at specified elevation"""
        if not self.meshes:
            return
        
        # Get bounds from all meshes
        bounds = self.meshes[0].bounds
        for mesh in self.meshes[1:]:
            mesh_bounds = mesh.bounds
            bounds = [min(bounds[0], mesh_bounds[0]), max(bounds[1], mesh_bounds[1]),
                     min(bounds[2], mesh_bounds[2]), max(bounds[3], mesh_bounds[3]),
                     min(bounds[4], mesh_bounds[4]), max(bounds[5], mesh_bounds[5])]
        
        # Create plane at mean elevation
        z_mean = (bounds[4] + bounds[5]) / 2
        
        plane = pv.Plane(center=(np.mean([bounds[0], bounds[1]]),
                                np.mean([bounds[2], bounds[3]]),
                                z_mean),
                        direction=(0, 0, 1),
                        i_size=bounds[1] - bounds[0],
                        j_size=bounds[3] - bounds[2])
        
        self.plotter.add_mesh(plane, 
                            color='gray',
                            opacity=0.3,
                            label="Reference Plane")
    
    def update_vertical_exaggeration(self, value):
        """Update vertical exaggeration"""
        self.vertical_exaggeration = value / 100.0
        self.exag_label.setText(f"{self.vertical_exaggeration:.1f}x")
        self.create_3d_sections()
    
    def update_opacity(self, value):
        """Update mesh opacity"""
        opacity = value / 100.0
        for actor in self.actors:
            actor.GetProperty().SetOpacity(opacity)
        self.plotter.render()
    
    def update_display(self):
        """Update display settings"""
        for actor in self.actors:
            if self.show_edges_cb.isChecked():
                actor.GetProperty().EdgeVisibilityOn()
            else:
                actor.GetProperty().EdgeVisibilityOff()
        
        if self.show_intersections_cb.isChecked():
            self.calculate_intersections()
        
        self.plotter.render()
    
    def toggle_grid(self, state):
        """Toggle grid visibility"""
        if state:
            self.plotter.show_grid()
        else:
            self.plotter.remove_bounds_axes()
    
    def update_texture(self):
        """Update section texture based on selection"""
        texture_type = self.texture_combo.currentText()
        
        for i, mesh in enumerate(self.meshes):
            if texture_type == "Elevation Gradient":
                self.plotter.remove_actor(self.actors[i])
                self.actors[i] = self.plotter.add_mesh(mesh,
                                                      scalars="Elevation",
                                                      cmap="terrain",
                                                      opacity=self.opacity_slider.value()/100,
                                                      show_edges=self.show_edges_cb.isChecked())
            elif texture_type == "Slope Gradient":
                if "Slope" in mesh.array_names:
                    self.plotter.remove_actor(self.actors[i])
                    self.actors[i] = self.plotter.add_mesh(mesh,
                                                          scalars="Slope",
                                                          cmap="RdYlBu",
                                                          opacity=self.opacity_slider.value()/100,
                                                          show_edges=self.show_edges_cb.isChecked())
            else:  # Solid Color
                color = self.section_colors['primary'] if i == 0 else self.section_colors['secondary']
                self.plotter.remove_actor(self.actors[i])
                self.actors[i] = self.plotter.add_mesh(mesh,
                                                      color=color,
                                                      opacity=self.opacity_slider.value()/100,
                                                      show_edges=self.show_edges_cb.isChecked())
    
    def pick_color(self, color_type):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.section_colors[color_type] = (color.redF(), color.greenF(), color.blueF())
            self.update_texture()
    
    def update_section_combo(self):
        """Update section selection combo box"""
        self.section_combo.clear()
        for i, profile in enumerate(self.profiles):
            name = profile.get('name', f'Section {i+1}')
            self.section_combo.addItem(name)
    
    def select_section(self, index):
        """Handle section selection"""
        if 0 <= index < len(self.actors):
            # Highlight selected section
            for i, actor in enumerate(self.actors):
                if i == index:
                    actor.GetProperty().SetOpacity(1.0)
                else:
                    actor.GetProperty().SetOpacity(0.5)
            self.plotter.render()
    
    def update_section_scale(self, value):
        """Update scale of selected section"""
        self.scale_factor = value
        # Recreate sections with new scale
        self.create_3d_sections()
    
    def on_point_picked(self, point):
        """Handle point picking in 3D view"""
        # Find closest point in profiles
        min_dist = float('inf')
        closest_info = None
        
        for i, profile in enumerate(self.profiles):
            if 'coordinates' in profile:
                coords = np.array(profile['coordinates'])
                elevations = np.array(profile['elevations']) * self.vertical_exaggeration
                
                # Create 3D points
                points_3d = np.column_stack([coords, elevations])
                
                # Find closest point
                distances = np.linalg.norm(points_3d - point, axis=1)
                min_idx = np.argmin(distances)
                
                if distances[min_idx] < min_dist:
                    min_dist = distances[min_idx]
                    closest_info = {
                        'section': i,
                        'point_index': min_idx,
                        'coordinates': coords[min_idx],
                        'elevation': profile['elevations'][min_idx],
                        'distance': profile['distances'][min_idx]
                    }
        
        if closest_info:
            # Update metadata table
            self.add_metadata_entry(closest_info)
            
            # Emit signal
            self.point_selected.emit((closest_info['coordinates'][0],
                                     closest_info['coordinates'][1],
                                     closest_info['elevation']))
    
    def add_metadata_entry(self, info):
        """Add entry to metadata table"""
        row = self.metadata_table.rowCount()
        self.metadata_table.insertRow(row)
        
        # Add data
        self.metadata_table.setItem(row, 0, QTableWidgetItem(f"P{row+1}"))
        self.metadata_table.setItem(row, 1, QTableWidgetItem(f"{info['coordinates'][0]:.2f}"))
        self.metadata_table.setItem(row, 2, QTableWidgetItem(f"{info['coordinates'][1]:.2f}"))
        self.metadata_table.setItem(row, 3, QTableWidgetItem(f"{info['elevation']:.2f}"))
        self.metadata_table.setItem(row, 4, QTableWidgetItem(f"Section {info['section']+1}"))
    
    def export_3d(self):
        """Export 3D scene"""
        filename, _ = QFileDialog.getSaveFileName(self, "Export 3D Scene", 
                                                 "", 
                                                 "VTK Files (*.vtk);;STL Files (*.stl);;OBJ Files (*.obj)")
        if filename:
            try:
                # Merge all meshes
                merged = self.meshes[0]
                for mesh in self.meshes[1:]:
                    merged = merged + mesh
                
                # Save based on extension
                if filename.endswith('.vtk'):
                    merged.save(filename)
                elif filename.endswith('.stl'):
                    merged.save(filename)
                elif filename.endswith('.obj'):
                    merged.save(filename)
                
                QMessageBox.information(self, "Success", f"3D scene exported to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export: {str(e)}")
    
    def set_view(self, view_type):
        """Set predefined camera views"""
        if view_type == 'top':
            self.plotter.view_xy()
        elif view_type == 'front':
            self.plotter.view_xz()
        elif view_type == 'side':
            self.plotter.view_yz()
        elif view_type == 'isometric':
            self.plotter.view_isometric()
        
        self.plotter.reset_camera()
    
    def get_profiles_from_project(self):
        """Get profile data from current QGIS project"""
        # This would interface with the main plugin to get current profile data
        # Placeholder for now - returns empty list
        return []
    
    def export_to_attribute_table(self):
        """Export metadata to QGIS attribute table"""
        if not self.metadata:
            return
        
        # Create memory layer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "3D Profile Metadata", "memory")
        provider = layer.dataProvider()
        
        # Add fields
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("x", QVariant.Double))
        fields.append(QgsField("y", QVariant.Double))
        fields.append(QgsField("z", QVariant.Double))
        fields.append(QgsField("section", QVariant.Int))
        fields.append(QgsField("notes", QVariant.String))
        provider.addAttributes(fields)
        layer.updateFields()
        
        # Add features
        features = []
        for i in range(self.metadata_table.rowCount()):
            feature = QgsFeature()
            x = float(self.metadata_table.item(i, 1).text())
            y = float(self.metadata_table.item(i, 2).text())
            
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
            feature.setAttributes([
                i + 1,
                x,
                y,
                float(self.metadata_table.item(i, 3).text()),
                int(self.metadata_table.item(i, 4).text().split()[-1]),
                self.metadata_table.item(i, 4).text() if self.metadata_table.item(i, 4) else ""
            ])
            features.append(feature)
        
        provider.addFeatures(features)
        QgsProject.instance().addMapLayer(layer)
        
        QMessageBox.information(self, "Success", "Metadata exported to attribute table")
    
    def add_perpendicular_section(self, line_geometry, profile_data):
        """Add a perpendicular section to the 3D view"""
        if not PYVISTA_AVAILABLE or not self.plotter:
            return
            
        try:
            # Extract points from line geometry
            if line_geometry.type() == QgsWkbTypes.LineGeometry:
                points = line_geometry.asPolyline()
                
                # Create 3D points for the section wall
                wall_points = []
                
                # Create points along the profile
                for i, (dist, elev) in enumerate(zip(profile_data['distances'], profile_data['elevations'])):
                    # Interpolate position along line
                    if len(points) >= 2:
                        t = dist / profile_data['distances'][-1]
                        x = points[0].x() + t * (points[1].x() - points[0].x())
                        y = points[0].y() + t * (points[1].y() - points[0].y())
                        
                        # Add point at elevation
                        wall_points.append([x, y, elev * self.vertical_exaggeration])
                
                if len(wall_points) > 1:
                    # Create polyline for the perpendicular section
                    wall_points_array = np.array(wall_points)
                    poly = pv.PolyData(wall_points_array)
                    poly["heights"] = wall_points_array[:, 2]
                    
                    # Create line
                    lines = []
                    for i in range(len(wall_points) - 1):
                        lines.extend([2, i, i + 1])
                    poly.lines = lines
                    
                    # Add to plotter with green color for perpendicular sections
                    self.plotter.add_mesh(
                        poly,
                        color='green',
                        line_width=3,
                        label=f'Perpendicular Section'
                    )
                    
                    # Store reference
                    if not hasattr(self, 'perpendicular_meshes'):
                        self.perpendicular_meshes = []
                    self.perpendicular_meshes.append(poly)
                    
                    # Update view
                    self.plotter.render()
                    
        except Exception as e:
            print(f"Error adding perpendicular section: {str(e)}")
    
    def show_installation_message(self):
        """Show message when PyVista is not installed"""
        layout = QVBoxLayout()
        
        msg = QLabel("PyVista is not installed. Please install it to use the advanced 3D viewer:\n\n"
                    "pip install pyvista pyvistaqt\n\n"
                    "Or use the Module Installer in the main plugin window.")
        msg.setWordWrap(True)
        layout.addWidget(msg)
        
        self.setLayout(layout)