# -*- coding: utf-8 -*-
"""
Dockable widget for Dual Profile Viewer
"""

from qgis.PyQt.QtWidgets import QDockWidget, QVBoxLayout, QWidget
from qgis.PyQt.QtCore import Qt
from .compact_dual_profile_viewer import CompactDualProfileViewer


class DualProfileDock(QDockWidget):
    """Dockable widget wrapper for the profile viewer"""
    
    def __init__(self, iface, parent=None):
        super().__init__("Dual Profile Viewer", parent)
        self.iface = iface
        
        # Set dock widget features
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setMinimumWidth(400)
        
        # Create container widget
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the compact profile viewer
        self.profile_viewer = CompactDualProfileViewer(self.iface, parent=container)
        
        layout.addWidget(self.profile_viewer)
        container.setLayout(layout)
        
        self.setWidget(container)
        
    def get_profile_viewer(self):
        """Get the embedded profile viewer"""
        return self.profile_viewer