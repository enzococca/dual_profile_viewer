# -*- coding: utf-8 -*-
"""
Polygon Profile Drawing Tool
Allows drawing rectangular or freehand polygon sections with width
"""

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsPointXY, QgsGeometry, QgsWkbTypes,
    QgsVectorLayer, QgsFeature,
    QgsProject, Qgis
)
from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsRubberBand
import math

class PolygonProfileTool(QgsMapTool):
    """Map tool for drawing polygon sections with width"""
    
    profile_created = pyqtSignal(object)  # Emits polygon geometry
    
    def __init__(self, canvas, iface):
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface
        self.rubber_band = None
        self.temp_rubber_band = None
        self.points = []
        self.drawing_mode = 'rectangle'  # 'rectangle', 'polygon', 'freehand'
        self.width = 10.0  # Default width in meters
        
    def set_drawing_mode(self, mode):
        """Set drawing mode: rectangle, polygon, or freehand"""
        self.drawing_mode = mode
        
    def set_width(self, width):
        """Set the width of the section"""
        self.width = width
        
    def canvasPressEvent(self, e):
        """Handle mouse press"""
        point = self.toMapCoordinates(e.pos())
        
        if e.button() == Qt.LeftButton:
            if self.drawing_mode == 'rectangle':
                self.handle_rectangle_click(point)
            elif self.drawing_mode == 'polygon':
                self.handle_polygon_click(point)
            elif self.drawing_mode == 'freehand':
                self.start_freehand(point)
                
        elif e.button() == Qt.RightButton:
            if self.drawing_mode == 'polygon' and len(self.points) >= 3:
                self.finish_polygon()
            else:
                self.reset()
                
    def handle_rectangle_click(self, point):
        """Handle rectangle drawing"""
        self.points.append(point)
        
        if len(self.points) == 1:
            # First point - start rubber band
            self.start_rubber_band()
        elif len(self.points) == 2:
            # Second point - create rectangle with width
            self.create_rectangle_section()
            
    def handle_polygon_click(self, point):
        """Handle polygon drawing"""
        self.points.append(point)
        
        if len(self.points) == 1:
            self.start_rubber_band()
        else:
            # Update rubber band
            self.update_rubber_band()
            
    def start_freehand(self, point):
        """Start freehand drawing"""
        self.points = [point]
        self.start_rubber_band()
        
    def canvasMoveEvent(self, e):
        """Handle mouse move"""
        if not self.points:
            return
            
        point = self.toMapCoordinates(e.pos())
        
        if self.drawing_mode == 'rectangle' and len(self.points) == 1:
            # Show preview rectangle
            self.show_rectangle_preview(point)
        elif self.drawing_mode == 'freehand':
            # Add point to freehand path
            self.points.append(point)
            self.update_rubber_band()
        elif self.drawing_mode == 'polygon' and len(self.points) > 0:
            # Show preview line
            self.show_polygon_preview(point)
            
    def canvasReleaseEvent(self, e):
        """Handle mouse release"""
        if self.drawing_mode == 'freehand' and self.points:
            # Finish freehand drawing
            self.create_freehand_section()
            
    def start_rubber_band(self):
        """Initialize rubber band"""
        self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0, 100))
        self.rubber_band.setWidth(2)
        self.rubber_band.setLineStyle(Qt.DashLine)
        
    def show_rectangle_preview(self, current_point):
        """Show preview of rectangle"""
        if self.temp_rubber_band:
            self.canvas.scene().removeItem(self.temp_rubber_band)
            
        self.temp_rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.temp_rubber_band.setColor(QColor(255, 0, 0, 50))
        self.temp_rubber_band.setWidth(1)
        
        # Create rectangle with width
        rect_points = self.create_rectangle_points(self.points[0], current_point)
        if rect_points:  # Only proceed if we have points
            for pt in rect_points:
                self.temp_rubber_band.addPoint(pt, False)
            self.temp_rubber_band.addPoint(rect_points[0], True)  # Close polygon
        
    def create_rectangle_points(self, p1, p2):
        """Create rectangle points with specified width"""
        # Calculate direction vector
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return []
            
        # Normalize direction
        dx /= length
        dy /= length
        
        # Perpendicular vector for width
        perp_x = -dy * self.width / 2
        perp_y = dx * self.width / 2
        
        # Four corners of rectangle
        corners = [
            QgsPointXY(p1.x() + perp_x, p1.y() + perp_y),
            QgsPointXY(p2.x() + perp_x, p2.y() + perp_y),
            QgsPointXY(p2.x() - perp_x, p2.y() - perp_y),
            QgsPointXY(p1.x() - perp_x, p1.y() - perp_y)
        ]
        
        return corners
        
    def create_rectangle_section(self):
        """Create rectangle section and emit"""
        if len(self.points) >= 2:
            rect_points = self.create_rectangle_points(self.points[0], self.points[1])
            
            # Create polygon geometry
            polygon = QgsGeometry.fromPolygonXY([rect_points])
            
            # Also create center line for profile extraction
            center_line = QgsGeometry.fromPolylineXY([self.points[0], self.points[1]])
            
            # Emit with both polygon and center line
            self.profile_created.emit({
                'polygon': polygon,
                'center_line': center_line,
                'width': self.width,
                'type': 'rectangle'
            })
            
            self.reset()
            
    def finish_polygon(self):
        """Finish polygon drawing"""
        if len(self.points) >= 3:
            # Create polygon
            polygon = QgsGeometry.fromPolygonXY([self.points])
            
            # Calculate center line (simplified - connects first and last point)
            center_line = QgsGeometry.fromPolylineXY([self.points[0], self.points[-1]])
            
            self.profile_created.emit({
                'polygon': polygon,
                'center_line': center_line,
                'width': None,  # Variable width
                'type': 'polygon'
            })
            
            self.reset()
            
    def create_freehand_section(self):
        """Create freehand section with buffer"""
        if len(self.points) >= 2:
            # Create line from points
            line = QgsGeometry.fromPolylineXY(self.points)
            
            # Buffer to create polygon with width
            polygon = line.buffer(self.width / 2, 5)
            
            self.profile_created.emit({
                'polygon': polygon,
                'center_line': line,
                'width': self.width,
                'type': 'freehand'
            })
            
            self.reset()
            
    def update_rubber_band(self):
        """Update rubber band with current points"""
        if self.rubber_band:
            self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
            for point in self.points:
                self.rubber_band.addPoint(point, False)
            if len(self.points) > 0:
                self.rubber_band.addPoint(self.points[0], True)  # Close polygon
                
    def show_polygon_preview(self, current_point):
        """Show preview line for polygon"""
        if self.temp_rubber_band:
            self.canvas.scene().removeItem(self.temp_rubber_band)
            
        self.temp_rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.temp_rubber_band.setColor(QColor(255, 0, 0, 200))
        self.temp_rubber_band.setWidth(2)
        self.temp_rubber_band.setLineStyle(Qt.DashLine)
        
        self.temp_rubber_band.addPoint(self.points[-1], False)
        self.temp_rubber_band.addPoint(current_point, True)
        
    def reset(self):
        """Reset the tool"""
        self.points = []
        
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
            
        if self.temp_rubber_band:
            self.canvas.scene().removeItem(self.temp_rubber_band)
            self.temp_rubber_band = None
            
        self.canvas.refresh()
        
    def deactivate(self):
        """Clean up when tool is deactivated"""
        self.reset()
        super().deactivate()