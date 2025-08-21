# -*- coding: utf-8 -*-
"""
Single Profile Drawing Tool
Allows drawing a single profile line for geological sections
"""

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsPointXY, QgsGeometry, QgsWkbTypes
from qgis.gui import QgsMapTool, QgsRubberBand

class SingleProfileTool(QgsMapTool):
    """Map tool for drawing a single profile line"""
    
    profile_created = pyqtSignal(object)  # Emits line geometry
    
    def __init__(self, canvas, iface):
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface
        self.rubber_band = None
        self.start_point = None
        self.is_drawing = False
        
    def canvasPressEvent(self, e):
        """Handle mouse press"""
        if e.button() == Qt.LeftButton:
            point = self.toMapCoordinates(e.pos())
            
            if not self.is_drawing:
                # Start drawing
                self.start_point = point
                self.is_drawing = True
                self.start_rubber_band()
            else:
                # Finish drawing
                self.finish_drawing(point)
                
        elif e.button() == Qt.RightButton:
            # Cancel drawing
            self.reset()
            
    def canvasMoveEvent(self, e):
        """Handle mouse move"""
        if self.is_drawing and self.start_point:
            end_point = self.toMapCoordinates(e.pos())
            self.update_rubber_band(end_point)
            
    def start_rubber_band(self):
        """Initialize rubber band for line preview"""
        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0))
        self.rubber_band.setWidth(2)
        
    def update_rubber_band(self, end_point):
        """Update rubber band preview"""
        if self.rubber_band and self.start_point:
            self.rubber_band.reset(QgsWkbTypes.LineGeometry)
            self.rubber_band.addPoint(self.start_point, False)
            self.rubber_band.addPoint(end_point, True)
            
    def finish_drawing(self, end_point):
        """Complete the line drawing"""
        if self.start_point:
            # Create line geometry
            line = QgsGeometry.fromPolylineXY([self.start_point, end_point])
            
            # Emit the created line
            self.profile_created.emit(line)
            
            # Reset tool
            self.reset()
            
    def reset(self):
        """Reset the tool"""
        self.is_drawing = False
        self.start_point = None
        
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
            
        self.canvas.refresh()
        
    def deactivate(self):
        """Clean up when tool is deactivated"""
        self.reset()
        super().deactivate()