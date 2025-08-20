# -*- coding: utf-8 -*-
"""
Multi-DEM selection widget with checkboxes
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QCheckBox, QScrollArea, QPushButton, QGroupBox)
from PyQt5.QtCore import pyqtSignal, Qt
from qgis.core import QgsProject, QgsRasterLayer


class MultiDEMWidget(QWidget):
    """Widget for selecting multiple DEMs to compare"""
    
    selection_changed = pyqtSignal(list)  # Emits list of selected layer IDs
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dem_checkboxes = {}
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Select DEMs to compare:"))
        
        # Select/Deselect all buttons
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        
        header_layout.addWidget(self.select_all_btn)
        header_layout.addWidget(self.deselect_all_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Scrollable area for DEM list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        
        # Container for checkboxes
        self.dem_container = QWidget()
        self.dem_layout = QVBoxLayout()
        self.dem_container.setLayout(self.dem_layout)
        
        scroll.setWidget(self.dem_container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
        # Load available DEMs
        self.refresh_dem_list()
        
    def refresh_dem_list(self):
        """Refresh the list of available DEMs"""
        # Clear existing checkboxes
        for checkbox in self.dem_checkboxes.values():
            checkbox.deleteLater()
        self.dem_checkboxes.clear()
        
        # Get all raster layers
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsRasterLayer) and layer.isValid():
                checkbox = QCheckBox(layer.name())
                checkbox.setProperty("layer_id", layer.id())
                checkbox.stateChanged.connect(self.on_selection_changed)
                
                self.dem_layout.addWidget(checkbox)
                self.dem_checkboxes[layer.id()] = checkbox
                
                # Select first DEM by default
                if len(self.dem_checkboxes) == 1:
                    checkbox.setChecked(True)
        
        # Add stretch at the end
        self.dem_layout.addStretch()
        
    def get_selected_layers(self):
        """Get list of selected layer IDs"""
        selected = []
        for layer_id, checkbox in self.dem_checkboxes.items():
            if checkbox.isChecked():
                selected.append(layer_id)
        return selected
        
    def on_selection_changed(self):
        """Handle checkbox state changes"""
        selected = self.get_selected_layers()
        self.selection_changed.emit(selected)
        
    def select_all(self):
        """Select all DEMs"""
        for checkbox in self.dem_checkboxes.values():
            checkbox.setChecked(True)
            
    def deselect_all(self):
        """Deselect all DEMs"""
        for checkbox in self.dem_checkboxes.values():
            checkbox.setChecked(False)
            
    def set_enabled(self, enabled):
        """Enable/disable the widget"""
        for checkbox in self.dem_checkboxes.values():
            checkbox.setEnabled(enabled)
        self.select_all_btn.setEnabled(enabled)
        self.deselect_all_btn.setEnabled(enabled)