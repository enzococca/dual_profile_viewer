# -*- coding: utf-8 -*-
"""
Geological/Stratigraphic 3D Section Viewer
Visualizes sections as geological walls with stratigraphic layers
"""

from qgis.PyQt import QtWidgets, QtCore
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                QWidget, QSlider, QLabel, QPushButton,
                                QGroupBox, QFormLayout, QComboBox,
                                QCheckBox, QSpinBox, QDoubleSpinBox,
                                QTableWidget, QTableWidgetItem,
                                QColorDialog, QInputDialog, QFileDialog)
from qgis.core import (QgsMessageLog, Qgis, QgsProject, QgsVectorLayer,
                      QgsRasterLayer, QgsPointXY)
from qgis.PyQt import QtWidgets
import numpy as np

try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False

class GeologicalSectionViewer(QDialog):
    """3D viewer for geological/stratigraphic sections"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Geological Section 3D Viewer")
        self.resize(1200, 800)
        
        # Data storage
        self.sections = []  # List of section data
        self.walls = []     # PyVista wall meshes
        self.wall_actors = []  # Actors for walls (for manipulation)
        self.layers = []    # Stratigraphic layers
        self.intersections = []
        self.reference_plane = None
        self.section_attributes = {}  # Store attributes for each section
        self.selected_actor = None
        self.selected_color = '#FF0000'  # Default red
        
        # Colors for different DEMs/layers
        self.layer_colors = {
            'primary': (0.8, 0.4, 0.2),      # Brown
            'layer1': (0.9, 0.7, 0.3),       # Sandy
            'layer2': (0.6, 0.6, 0.6),       # Gray
            'layer3': (0.4, 0.2, 0.1),       # Dark brown
            'layer4': (0.7, 0.5, 0.3),       # Medium brown
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        layout = QVBoxLayout()
        
        if not PYVISTA_AVAILABLE:
            label = QLabel("PyVista not available. Install with: pip install pyvista pyvistaqt")
            layout.addWidget(label)
            self.setLayout(layout)
            return
        
        # Create main horizontal layout
        main_layout = QHBoxLayout()
        
        # Left side - 3D viewer
        viewer_widget = QWidget()
        viewer_layout = QVBoxLayout()
        
        # PyVista plotter
        self.plotter = QtInteractor(viewer_widget)
        # Enable picking
        self.plotter.enable_point_picking(callback=self.on_point_picked, show_message=False)
        viewer_layout.addWidget(self.plotter.interactor)
        
        viewer_widget.setLayout(viewer_layout)
        main_layout.addWidget(viewer_widget, 3)
        
        # Right side - controls
        control_widget = QWidget()
        control_widget.setMaximumWidth(400)
        control_layout = QVBoxLayout()
        
        # Section controls
        section_group = QGroupBox("Section Controls")
        section_layout = QFormLayout()
        
        # Wall thickness
        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setRange(1, 100)
        self.thickness_slider.setValue(20)
        self.thickness_slider.valueChanged.connect(self.update_wall_thickness)
        self.thickness_label = QLabel("20 m")
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(self.thickness_slider)
        thickness_layout.addWidget(self.thickness_label)
        section_layout.addRow("Wall Thickness:", thickness_layout)
        
        # Vertical exaggeration
        self.exag_slider = QSlider(Qt.Horizontal)
        self.exag_slider.setRange(1, 50)
        self.exag_slider.setValue(10)
        self.exag_slider.valueChanged.connect(self.update_vertical_exaggeration)
        self.exag_label = QLabel("1.0x")
        exag_layout = QHBoxLayout()
        exag_layout.addWidget(self.exag_slider)
        exag_layout.addWidget(self.exag_label)
        section_layout.addRow("Vertical Scale:", exag_layout)
        
        # Show layers checkbox
        self.show_layers_cb = QCheckBox("Show Stratigraphic Layers")
        self.show_layers_cb.setChecked(True)
        self.show_layers_cb.toggled.connect(self.toggle_layers)
        section_layout.addRow(self.show_layers_cb)
        
        # Show intersections
        self.show_intersections_cb = QCheckBox("Show Intersections")
        self.show_intersections_cb.setChecked(True)
        self.show_intersections_cb.toggled.connect(self.toggle_intersections)
        section_layout.addRow(self.show_intersections_cb)
        
        section_group.setLayout(section_layout)
        control_layout.addWidget(section_group)
        
        # Reference plane controls
        plane_group = QGroupBox("Reference Plane")
        plane_layout = QFormLayout()
        
        # Plane elevation
        self.plane_elevation = QDoubleSpinBox()
        self.plane_elevation.setRange(-1000, 5000)
        self.plane_elevation.setValue(0)
        self.plane_elevation.setSuffix(" m")
        self.plane_elevation.valueChanged.connect(self.update_reference_plane)
        plane_layout.addRow("Elevation:", self.plane_elevation)
        
        # Plane opacity
        self.plane_opacity = QSlider(Qt.Horizontal)
        self.plane_opacity.setRange(0, 100)
        self.plane_opacity.setValue(30)
        self.plane_opacity.valueChanged.connect(self.update_plane_opacity)
        plane_layout.addRow("Opacity:", self.plane_opacity)
        
        # Show/hide plane
        self.show_plane_cb = QCheckBox("Show Reference Plane")
        self.show_plane_cb.toggled.connect(self.toggle_reference_plane)
        plane_layout.addRow(self.show_plane_cb)
        
        plane_group.setLayout(plane_layout)
        control_layout.addWidget(plane_group)
        
        # Section import
        import_group = QGroupBox("Import Sections")
        import_layout = QVBoxLayout()
        
        self.layer_combo = QComboBox()
        self.refresh_layers_btn = QPushButton("Refresh Layers")
        self.refresh_layers_btn.clicked.connect(self.refresh_section_layers)
        self.import_btn = QPushButton("Import Selected Layer")
        self.import_btn.clicked.connect(self.import_section_layer)
        
        import_layout.addWidget(QLabel("Section Layer:"))
        import_layout.addWidget(self.layer_combo)
        import_layout.addWidget(self.refresh_layers_btn)
        import_layout.addWidget(self.import_btn)
        
        import_group.setLayout(import_layout)
        control_layout.addWidget(import_group)
        
        # Refresh layers on startup
        self.refresh_section_layers()
        
        # Layer attributes
        attr_group = QGroupBox("Section Attributes")
        attr_layout = QVBoxLayout()
        
        # Layer table
        self.layer_table = QTableWidget()
        self.layer_table.setColumnCount(4)
        self.layer_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Color"])
        self.layer_table.setSelectionBehavior(QTableWidget.SelectRows)
        attr_layout.addWidget(self.layer_table)
        
        # Color controls
        color_layout = QHBoxLayout()
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_section_color)
        self.apply_color_btn = QPushButton("Apply Color")
        self.apply_color_btn.clicked.connect(self.apply_section_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(self.apply_color_btn)
        attr_layout.addLayout(color_layout)
        
        # Info label
        self.info_label = QLabel("Click on a 3D section to select it")
        self.info_label.setWordWrap(True)
        attr_layout.addWidget(self.info_label)
        
        attr_group.setLayout(attr_layout)
        control_layout.addWidget(attr_group)
        
        # View controls
        view_group = QGroupBox("View Controls")
        view_layout = QVBoxLayout()
        
        view_btn_layout = QHBoxLayout()
        top_btn = QPushButton("Top")
        top_btn.clicked.connect(lambda: self.set_view('top'))
        front_btn = QPushButton("Front")
        front_btn.clicked.connect(lambda: self.set_view('front'))
        side_btn = QPushButton("Side")
        side_btn.clicked.connect(lambda: self.set_view('side'))
        iso_btn = QPushButton("3D")
        iso_btn.clicked.connect(lambda: self.set_view('iso'))
        
        view_btn_layout.addWidget(top_btn)
        view_btn_layout.addWidget(front_btn)
        view_btn_layout.addWidget(side_btn)
        view_btn_layout.addWidget(iso_btn)
        view_layout.addLayout(view_btn_layout)
        
        view_group.setLayout(view_layout)
        control_layout.addWidget(view_group)
        
        # Export button
        export_btn = QPushButton("Export 3D Model")
        export_btn.clicked.connect(self.export_3d)
        control_layout.addWidget(export_btn)
        
        control_layout.addStretch()
        control_widget.setLayout(control_layout)
        main_layout.addWidget(control_widget, 1)
        
        layout.addLayout(main_layout)
        self.setLayout(layout)
        
        # Initialize 3D scene
        self.setup_3d_scene()
        
    def setup_3d_scene(self):
        """Initialize the 3D scene"""
        self.plotter.set_background('white')
        self.plotter.show_axes()
        self.plotter.add_axes()
        
    def load_sections(self, profile_data_list):
        """Load profile sections data"""
        self.sections = []
        
        # Process each pair of profiles as a wall section
        for i in range(0, len(profile_data_list), 2):
            if i + 1 < len(profile_data_list):
                section = {
                    'top': profile_data_list[i],
                    'bottom': profile_data_list[i + 1],
                    'name': f'Wall {i//2 + 1}'
                }
                self.sections.append(section)
        
        self.create_geological_walls()
        
    def create_geological_walls(self):
        """Create 3D wall meshes from section data"""
        self.plotter.clear()
        self.walls = []
        self.wall_actors = []  # Store actors for later manipulation
        
        for idx, section in enumerate(self.sections):
            result = self.create_wall_mesh(section, idx)
            if result and result[0] is not None:
                wall_mesh, wall_actor = result
                self.walls.append(wall_mesh)
                self.wall_actors.append(wall_actor)
                
        # Calculate intersections
        self.calculate_wall_intersections()
        
        # Add reference plane if enabled
        if self.show_plane_cb.isChecked():
            self.add_reference_plane()
            
        self.plotter.reset_camera()
        
    def create_wall_mesh(self, section, wall_idx):
        """Create a 3D wall mesh from top and bottom profiles"""
        try:
            from .wall_intersection_utils import create_wall_from_profiles
            
            top_profile = section['top']
            bottom_profile = section['bottom']
            
            # Get the wall thickness setting
            thickness = self.thickness_slider.value()
            
            # Use utility function to create wall
            mesh = create_wall_from_profiles(top_profile, bottom_profile, thickness=None)
            
            # Apply vertical exaggeration
            exag = self.exag_slider.value() / 10.0
            mesh.points[:, 2] *= exag
            
            # Get color from attributes if available
            color = self.layer_colors['primary']
            if 'color' in section:
                color = section['color']
            elif 'type' in section and section['type'] == 'Lower':
                color = 'blue'
            
            # If we have multiple DEMs, create layers
            if self.show_layers_cb.isChecked() and len(self.sections) > 1:
                actor = self.add_stratigraphic_layers(mesh, section, wall_idx)
            else:
                # Single color wall
                actor = self.plotter.add_mesh(mesh, 
                                    color=color,
                                    opacity=0.8,
                                    show_edges=True,
                                    label=section['name'],
                                    pickable=True)  # Make pickable
            
            return mesh, actor
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error creating wall mesh: {str(e)}", 
                                   "DualProfileViewer", Qgis.Warning)
            return None, None
    
    def add_stratigraphic_layers(self, mesh, section, wall_idx):
        """Add colored stratigraphic layers to the wall"""
        # This is where we would add different colored layers based on 
        # different DEM surfaces or geological interpretations
        
        # For now, color by elevation bands
        z_min = mesh.points[:, 2].min()
        z_max = mesh.points[:, 2].max()
        z_range = z_max - z_min
        
        # Create elevation bands
        n_bands = 4
        band_colors = ['#8B4513', '#D2B48C', '#808080', '#654321']  # Use hex colors
        
        actor = None
        for i in range(n_bands):
            band_min = z_min + (i * z_range / n_bands)
            band_max = z_min + ((i + 1) * z_range / n_bands)
            
            # Extract cells in this elevation band
            band_mesh = mesh.threshold([band_min, band_max], scalars="Elevation")
            
            if band_mesh.n_cells > 0:
                band_actor = self.plotter.add_mesh(band_mesh,
                                    color=band_colors[i % len(band_colors)],
                                    opacity=0.8,
                                    show_edges=True,
                                    label=f"{section['name']} Layer {i+1}",
                                    pickable=True)
                if i == 0:  # Return first actor as main
                    actor = band_actor
        
        return actor if actor else self.plotter.add_mesh(mesh, pickable=True)
    
    def calculate_wall_intersections(self):
        """Calculate intersections between walls"""
        if not self.show_intersections_cb.isChecked():
            return
            
        self.intersections = []
        
        # Check each pair of walls
        for i in range(len(self.walls)):
            for j in range(i + 1, len(self.walls)):
                try:
                    intersection = self.walls[i].intersection(self.walls[j])
                    if intersection and hasattr(intersection, 'points') and len(intersection.points) > 0:
                        self.intersections.append(intersection)
                        # Add intersection as highlighted line
                        self.plotter.add_mesh(intersection,
                                            color='red',
                                            line_width=5,
                                            label=f"Intersection {i+1}-{j+1}")
                except Exception as e:
                    QgsMessageLog.logMessage(f"Error calculating intersections: {str(e)}", 
                                           "DualProfileViewer", Qgis.Warning)
    
    def add_reference_plane(self):
        """Add a horizontal reference plane"""
        if not self.walls:
            return
            
        # Get bounds from all walls
        all_points = []
        for wall in self.walls:
            all_points.extend(wall.points)
        all_points = np.array(all_points)
        
        x_min, x_max = all_points[:, 0].min(), all_points[:, 0].max()
        y_min, y_max = all_points[:, 1].min(), all_points[:, 1].max()
        
        # Extend bounds by 10%
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_min -= 0.1 * x_range
        x_max += 0.1 * x_range
        y_min -= 0.1 * y_range
        y_max += 0.1 * y_range
        
        # Create plane at specified elevation
        z = self.plane_elevation.value() * (self.exag_slider.value() / 10.0)
        
        plane = pv.Plane(center=(np.mean([x_min, x_max]), 
                                np.mean([y_min, y_max]), 
                                z),
                        direction=(0, 0, 1),
                        i_size=x_max - x_min,
                        j_size=y_max - y_min)
        
        self.reference_plane = self.plotter.add_mesh(plane,
                                                    color='lightblue',
                                                    opacity=self.plane_opacity.value()/100,
                                                    label="Reference Plane")
    
    def update_wall_thickness(self, value):
        """Update wall thickness display"""
        self.thickness_label.setText(f"{value} m")
        # In a real implementation, this would recreate the walls with new thickness
        
    def update_vertical_exaggeration(self, value):
        """Update vertical exaggeration"""
        self.exag_label.setText(f"{value/10:.1f}x")
        self.create_geological_walls()
        
    def toggle_layers(self, checked):
        """Toggle stratigraphic layer visualization"""
        self.create_geological_walls()
        
    def toggle_intersections(self, checked):
        """Toggle intersection visualization"""
        self.create_geological_walls()
        
    def toggle_reference_plane(self, checked):
        """Toggle reference plane visibility"""
        if checked:
            self.add_reference_plane()
        else:
            if self.reference_plane:
                self.plotter.remove_actor(self.reference_plane)
                
    def update_reference_plane(self, value):
        """Update reference plane elevation"""
        if self.show_plane_cb.isChecked():
            if self.reference_plane:
                self.plotter.remove_actor(self.reference_plane)
            self.add_reference_plane()
            
    def update_plane_opacity(self, value):
        """Update reference plane opacity"""
        if self.reference_plane:
            self.reference_plane.GetProperty().SetOpacity(value/100)
            self.plotter.render()
            
    def add_layer_attribute(self):
        """Add attribute to selected layer"""
        # Get layer name
        layer_name, ok = QInputDialog.getText(self, "Layer Name", "Enter layer name:")
        if not ok:
            return
            
        # Get notes
        notes, ok = QInputDialog.getText(self, "Layer Notes", "Enter notes/attributes:")
        if not ok:
            return
            
        # Add to table
        row = self.layer_table.rowCount()
        self.layer_table.insertRow(row)
        self.layer_table.setItem(row, 0, QTableWidgetItem(f"Layer {row+1}"))
        self.layer_table.setItem(row, 1, QTableWidgetItem(layer_name))
        
        # Color button
        color_btn = QPushButton("Choose")
        color_btn.clicked.connect(lambda: self.choose_layer_color(row))
        self.layer_table.setCellWidget(row, 2, color_btn)
        
        self.layer_table.setItem(row, 3, QTableWidgetItem(notes))
        
    def choose_layer_color(self, row):
        """Choose color for a layer"""
        color = QColorDialog.getColor()
        if color.isValid():
            # Update color button
            btn = self.layer_table.cellWidget(row, 2)
            btn.setStyleSheet(f"background-color: {color.name()}")
            
    def set_view(self, view_type):
        """Set camera view"""
        if view_type == 'top':
            self.plotter.view_xy()
        elif view_type == 'front':
            self.plotter.view_xz()
        elif view_type == 'side':
            self.plotter.view_yz()
        elif view_type == 'iso':
            self.plotter.view_isometric()
            
        self.plotter.reset_camera()
        
    def choose_section_color(self):
        """Open color dialog to choose section color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self.selected_color}")
    
    def apply_section_color(self):
        """Apply selected color to current section"""
        if not hasattr(self, 'selected_section_idx'):
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a section first")
            return
            
        if not hasattr(self, 'selected_color'):
            QtWidgets.QMessageBox.warning(self, "Warning", "Please choose a color first")
            return
            
        self.color_section_by_attribute(self.selected_section_idx, self.selected_color)
        
        # Update table
        self.update_section_table()
    
    def update_section_table(self):
        """Update the section attributes table"""
        self.layer_table.setRowCount(len(self.sections))
        
        for i, section in enumerate(self.sections):
            # ID
            self.layer_table.setItem(i, 0, QTableWidgetItem(str(i)))
            
            # Name
            self.layer_table.setItem(i, 1, QTableWidgetItem(section.get('name', f'Section {i}')))
            
            # Type
            self.layer_table.setItem(i, 2, QTableWidgetItem(section.get('type', 'Upper')))
            
            # Color
            color = section.get('color', '#FF0000')
            color_item = QTableWidgetItem(color)
            from qgis.PyQt.QtGui import QColor
            color_item.setBackground(QColor(color))
            self.layer_table.setItem(i, 3, color_item)
    
    def export_3d(self):
        """Export 3D model"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export 3D Model",
            "geological_section.stl",
            "STL Files (*.stl);;OBJ Files (*.obj);;VTK Files (*.vtk)"
        )
        
        if filename:
            try:
                # Merge all meshes
                merged = self.walls[0]
                for wall in self.walls[1:]:
                    merged = merged + wall
                    
                merged.save(filename)
                QtWidgets.QMessageBox.information(self, "Success", 
                                                f"3D model exported to {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", 
                                              f"Failed to export: {str(e)}")
    
    def refresh_section_layers(self):
        """Refresh the list of available section layers"""
        self.layer_combo.clear()
        
        # Look for line layers that might contain sections
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 1:  # Line
                if any(keyword in layer.name().lower() for keyword in ['section', 'profile', 'sezione']):
                    self.layer_combo.addItem(layer.name(), layer.id())
    
    def import_section_layer(self):
        """Import sections from selected layer"""
        layer_id = self.layer_combo.currentData()
        if not layer_id:
            return
            
        layer = QgsProject.instance().mapLayer(layer_id)
        if not layer:
            return
            
        # Clear existing sections
        self.sections = []
        self.section_attributes = {}
        
        # Get the main DEM
        from qgis.core import QgsRasterLayer
        dem_layers = [l for l in QgsProject.instance().mapLayers().values() 
                     if isinstance(l, QgsRasterLayer)]
        if not dem_layers:
            QtWidgets.QMessageBox.warning(self, "Warning", "No DEM layers found")
            return
            
        # Extract profiles from features
        for feature in layer.getFeatures():
            geom = feature.geometry()
            if geom:
                # Extract profile along the line
                line_points = []
                if geom.isMultipart():
                    for part in geom.asMultiPolyline():
                        line_points.extend(part)
                else:
                    line_points = geom.asPolyline()
                    
                if len(line_points) >= 2:
                    # Sample elevation along line
                    profile_data = self.sample_elevation_along_line(dem_layers[0], line_points)
                    
                    # Get feature attributes
                    attrs = feature.attributes()
                    field_names = [field.name() for field in layer.fields()]
                    
                    # Extract specific attributes
                    label = 'Section'
                    section_type = 'Upper'
                    if 'label' in field_names:
                        label = feature['label']
                    if 'type' in field_names:
                        section_type = feature['type']
                    
                    # Create bottom profile (offset down)
                    bottom_profile = profile_data.copy()
                    bottom_profile['elevations'] = [e - 50 for e in profile_data['elevations']]  # 50m depth
                    
                    # Store section with attributes
                    section = {
                        'name': label,
                        'top': profile_data,
                        'bottom': bottom_profile,
                        'type': section_type,
                        'attributes': attrs,
                        'feature_id': feature.id()
                    }
                    
                    self.sections.append(section)
                    self.section_attributes[feature.id()] = attrs
        
        # Create 3D visualization
        if self.sections:
            self.create_geological_walls()
            self.update_section_table()  # Update the attributes table
            QtWidgets.QMessageBox.information(self, "Success", 
                f"Imported {len(self.sections)} sections from {layer.name()}")
    
    def sample_elevation_along_line(self, raster_layer, line_points, num_samples=100):
        """Sample elevation values along a line"""
        import numpy as np
        from qgis.core import QgsPointXY
        
        # Interpolate points along line
        distances = []
        total_distance = 0
        
        for i in range(1, len(line_points)):
            dist = line_points[i-1].distance(line_points[i])
            total_distance += dist
            distances.append(total_distance)
        
        # Sample at regular intervals
        sample_distances = np.linspace(0, total_distance, num_samples)
        sampled_points = []
        elevations = []
        coordinates = []
        
        for sample_dist in sample_distances:
            # Find which segment contains this distance
            cumulative = 0
            for i in range(len(distances)):
                if cumulative + distances[i] >= sample_dist:
                    # Interpolate within this segment
                    t = (sample_dist - cumulative) / distances[i] if distances[i] > 0 else 0
                    p1 = line_points[i]
                    p2 = line_points[i+1]
                    
                    x = p1.x() + t * (p2.x() - p1.x())
                    y = p1.y() + t * (p2.y() - p1.y())
                    
                    point = QgsPointXY(x, y)
                    sampled_points.append(point)
                    coordinates.append([x, y])
                    
                    # Sample raster at this point
                    value = raster_layer.dataProvider().sample(point, 1)[0]
                    elevations.append(value if value is not None else 0)
                    break
                cumulative += distances[i]
        
        return {
            'distances': sample_distances.tolist(),
            'elevations': elevations,
            'coordinates': coordinates
        }
    
    def on_point_picked(self, point):
        """Handle point picking in 3D view"""
        if point is not None:
            # Find closest section to the picked point
            min_dist = float('inf')
            closest_section = None
            
            for i, section in enumerate(self.sections):
                if 'coordinates' in section.get('top', {}):
                    coords = np.array(section['top']['coordinates'])
                    # Calculate distance to section
                    for coord in coords:
                        dist = np.linalg.norm(np.array([coord[0], coord[1], 0]) - 
                                            np.array([point[0], point[1], 0]))
                        if dist < min_dist:
                            min_dist = dist
                            closest_section = i
            
            if closest_section is not None and min_dist < 100:  # 100m threshold
                self.show_section_attributes(closest_section)
    
    def show_section_attributes(self, section_idx):
        """Display attributes for selected section"""
        if section_idx < len(self.sections):
            self.selected_section_idx = section_idx
            section = self.sections[section_idx]
            
            # Update info label
            self.info_label.setText(f"Selected: {section.get('name', f'Section {section_idx}')}")
            
            # Highlight selected row in table
            self.layer_table.selectRow(section_idx)
            
            # Update the entire table
            self.update_section_table()
    
    def color_section_by_attribute(self, section_idx, color):
        """Color a section based on attribute"""
        if section_idx < len(self.wall_actors) and self.wall_actors[section_idx]:
            # Remove old actor
            self.plotter.remove_actor(self.wall_actors[section_idx])
            
            # Re-add with new color
            self.wall_actors[section_idx] = self.plotter.add_mesh(
                self.walls[section_idx],
                color=color,
                opacity=0.8,
                show_edges=True,
                label=self.sections[section_idx]['name'],
                pickable=True
            )
            
            # Store color in section data
            self.sections[section_idx]['color'] = color
            self.plotter.render()