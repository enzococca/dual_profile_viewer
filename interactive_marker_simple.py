# -*- coding: utf-8 -*-
"""
Simple Interactive Section Marker
A safer implementation using composition instead of multiple inheritance
"""

from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, QPointF, QTimer, QRectF, QPoint
from qgis.PyQt.QtGui import QColor, QPen, QBrush, QPainter
from qgis.PyQt.QtWidgets import QInputDialog
from qgis.core import (
    QgsPointXY, QgsGeometry, QgsWkbTypes, 
    QgsMessageLog, Qgis
)
from qgis.gui import QgsMapCanvasItem, QgsRubberBand
import math


class MarkerSignals(QObject):
    """Separate class for Qt signals"""
    position_changed = pyqtSignal(float)
    perpendicular_requested = pyqtSignal(QgsPointXY, float, float)


class SimpleInteractiveMarker(QgsMapCanvasItem):
    """Simple marker that can be dragged along a section line"""
    
    def __init__(self, canvas, section_line):
        super().__init__(canvas)
        
        # Signal handler
        self.signals = MarkerSignals()
        
        self.canvas = canvas
        self.section_line = self._ensure_geometry(section_line)
        self.normalized_position = 0.0
        self.marker_radius = 10
        
        # Visual properties
        self.normal_color = QColor(255, 0, 0, 200)  # Red when inactive
        self.active_color = QColor(0, 255, 0, 200)  # Green when active
        self.hover_color = QColor(255, 100, 100, 255)
        self.current_color = self.normal_color
        
        # Marker state
        self.is_active = False  # Marker follows mouse when active
        self.last_mouse_pos = None
        
        # Perpendicular preview
        self.perpendicular_preview = QgsRubberBand(canvas, QgsWkbTypes.LineGeometry)
        self.perpendicular_preview.setColor(QColor(0, 255, 0, 150))
        self.perpendicular_preview.setWidth(2)
        
        # Initial position
        self.update_position(0.0)
        
        # Connect to canvas events for refresh
        canvas.extentsChanged.connect(self.canvas_extent_changed)
        canvas.destinationCrsChanged.connect(self.canvas_extent_changed)
        
        # Make item interactive
        self.setFlag(self.ItemIsMovable, False)  # We handle movement ourselves
        self.setAcceptHoverEvents(True)
        
    def _ensure_geometry(self, line):
        """Ensure line is a QgsGeometry"""
        if isinstance(line, list):
            return QgsGeometry.fromPolylineXY(line)
        return line
        
    def canvas_extent_changed(self):
        """Handle canvas extent changes (zoom/pan)"""
        # Re-update position to adjust to new canvas coordinates
        self.update_position(self.normalized_position)
        
    def update_section_line(self, new_line):
        """Update the section line"""
        self.section_line = self._ensure_geometry(new_line)
        self.update_position(self.normalized_position)
        
    def update_position(self, normalized_pos):
        """Update marker position (0-1 along line)"""
        self.normalized_position = max(0.0, min(1.0, normalized_pos))
        
        if not self.section_line or self.section_line.isEmpty():
            return
            
        try:
            length = self.section_line.length()
            distance = length * self.normalized_position
            
            # Get point at distance
            point = self.section_line.interpolate(distance)
            if point and not point.isEmpty():
                # Convert to canvas coordinates
                map_point = point.asPoint()
                canvas_point = self.canvas.mapSettings().mapToPixel().transform(map_point)
                self.setPos(canvas_point.x(), canvas_point.y())
                self.show()
                
        except Exception as e:
            QgsMessageLog.logMessage(f"Error updating marker position: {str(e)}", 
                                   "DualProfileViewer", Qgis.Warning)
                                   
    def get_current_point(self):
        """Get current point on line"""
        if not self.section_line or self.section_line.isEmpty():
            return None
            
        try:
            length = self.section_line.length()
            distance = length * self.normalized_position
            point = self.section_line.interpolate(distance)
            if point and not point.isEmpty():
                return point.asPoint()
        except:
            pass
        return None
        
    def find_closest_position(self, map_point):
        """Find closest position on line to given point"""
        if not self.section_line or self.section_line.isEmpty():
            return 0.0
            
        try:
            # Use QGIS built-in method
            result = self.section_line.closestSegmentWithContext(map_point)
            
            # result is a tuple: (distance, QgsPointXY, vertex_index, ...)
            if result[0] < 0 or len(result) < 2:
                return self.normalized_position
                
            # Get the closest point
            closest_point = result[1]
            if not isinstance(closest_point, QgsPointXY):
                # If it's not a QgsPointXY, try to create one
                QgsMessageLog.logMessage(f"Unexpected closest point type: {type(closest_point)}", "DualProfileViewer", Qgis.Warning)
                return self.normalized_position
            
            # Find normalized position by sampling
            length = self.section_line.length()
            if length <= 0:
                return 0.0
                
            min_dist = float('inf')
            best_pos = 0.0
            
            # Sample at 50 points along line for better performance
            for i in range(51):
                pos = i / 50.0
                dist = length * pos
                test_point = self.section_line.interpolate(dist)
                if test_point and not test_point.isEmpty():
                    d = closest_point.distance(test_point.asPoint())
                    if d < min_dist:
                        min_dist = d
                        best_pos = pos
                        
            return best_pos
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error in find_closest_position: {str(e)}", "DualProfileViewer", Qgis.Warning)
            return self.normalized_position
        
    def paint(self, painter, option, widget):
        """Paint the marker"""
        painter.save()
        try:
            if not self.get_current_point():
                return
                
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Outer ring if active
            if self.is_active:
                painter.setPen(QPen(QColor(0, 255, 0, 100), 4))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(QPointF(0, 0), self.marker_radius + 4, self.marker_radius + 4)
            
            # Shadow
            painter.setPen(QPen(QColor(0, 0, 0, 50), 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(0, 0), self.marker_radius + 1, self.marker_radius + 1)
            
            # Main circle
            painter.setPen(QPen(self.current_color, 3))
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.drawEllipse(QPointF(0, 0), self.marker_radius, self.marker_radius)
            
            # Center dot
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(self.current_color))
            painter.drawEllipse(QPointF(0, 0), 4, 4)
            
        except Exception as e:
            pass
        finally:
            painter.restore()
            
    def boundingRect(self):
        """Bounding rectangle for the item"""
        r = self.marker_radius + 3
        return QRectF(-r, -r, 2*r, 2*r)
        
    def mousePressEvent(self, event):
        """Handle mouse press - not used in new implementation"""
        pass
            
    def mouseMoveEvent(self, event):
        """Handle mouse move - not used in new implementation"""
        pass
                
    def mouseReleaseEvent(self, event):
        """Handle mouse release - not used in new implementation"""
        pass
            
    def hoverEnterEvent(self, event):
        """Handle mouse hover enter"""
        if not self.is_active:
            self.current_color = self.hover_color
            self.update()
            
    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave"""  
        if not self.is_active:
            self.current_color = self.normal_color
        else:
            self.current_color = self.active_color
        self.update()
            
    def set_visible(self, visible):
        """Set visibility"""
        if visible:
            self.show()
        else:
            self.hide()
            if self.perpendicular_preview:
                self.perpendicular_preview.hide()
                
    def toggle_active(self):
        """Toggle marker active state"""
        self.is_active = not self.is_active
        if self.is_active:
            self.current_color = self.active_color  # Use active color (green)
            self.setVisible(True)  # Make sure marker is visible
            self.show()  # Make sure marker is visible
            QgsMessageLog.logMessage("Marker activated - move mouse to position, right-click to create perpendicular", "DualProfileViewer", Qgis.Info)
        else:
            self.current_color = self.normal_color
            self.setVisible(True)  # Keep marker visible but red
            self.show()  # Show with red color
            QgsMessageLog.logMessage("Marker deactivated", "DualProfileViewer", Qgis.Info)
        self.update()
        
    def handle_mouse_move(self, map_point):
        """Handle mouse movement when marker is active"""
        if not self.is_active:
            return
            
        try:
            # Find closest position on line
            new_pos = self.find_closest_position(map_point)
            if abs(new_pos - self.normalized_position) > 0.001:  # Small threshold to avoid too many updates
                self.update_position(new_pos)
                self.signals.position_changed.emit(new_pos)
        except Exception as e:
            QgsMessageLog.logMessage(f"Error in handle_mouse_move: {str(e)}", "DualProfileViewer", Qgis.Warning)
                
    def create_perpendicular_section(self):
        """Create perpendicular section at current position"""
        # Get current point and angle
        point = self.get_current_point()
        if not point:
            return False
            
        # Calculate perpendicular angle
        angle = self.get_perpendicular_angle()
        
        # Ask for length
        length, ok = QInputDialog.getDouble(
            None,
            "Perpendicular Section",
            "Enter length of perpendicular section (meters):",
            value=50.0,
            min=1.0,
            max=1000.0,
            decimals=1
        )
        
        if ok and length > 0:
            self.signals.perpendicular_requested.emit(point, angle, length)
            QgsMessageLog.logMessage(f"Creating perpendicular section: {length}m", "DualProfileViewer", Qgis.Info)
            return True
            
        return False
        
    def get_perpendicular_angle(self):
        """Get angle perpendicular to line at current position"""
        if not self.section_line or self.section_line.isEmpty():
            return 0.0
            
        try:
            length = self.section_line.length()
            distance = length * self.normalized_position
            
            # Get points slightly before and after
            delta = min(1.0, length * 0.01)
            dist1 = max(0, distance - delta)
            dist2 = min(length, distance + delta)
            
            p1 = self.section_line.interpolate(dist1)
            p2 = self.section_line.interpolate(dist2)
            
            if p1 and p2 and not p1.isEmpty() and not p2.isEmpty():
                dx = p2.asPoint().x() - p1.asPoint().x()
                dy = p2.asPoint().y() - p1.asPoint().y()
                angle = math.atan2(dy, dx)
                return angle + math.pi / 2  # Perpendicular
                
        except:
            pass
            
        return 0.0


class InteractiveMarkerController(QObject):
    """Controller to manage the marker and handle events"""
    
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.marker = None
        self.section_line = None
        self.enabled = True  # Add flag to enable/disable controller
        
        # Install event filter on canvas viewport for better event capture
        self.canvas.installEventFilter(self)
        if hasattr(self.canvas, 'viewport'):
            self.canvas.viewport().installEventFilter(self)
            
        # Timer for tracking mouse position when active
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_marker_position)
        self.update_timer.setInterval(50)  # Update every 50ms
        
    def create_marker(self, section_line):
        """Create or update the marker"""
        if self.marker:
            self.marker.update_section_line(section_line)
        else:
            self.marker = SimpleInteractiveMarker(self.canvas, section_line)
            
        self.section_line = section_line
        return self.marker
        
    def update_marker_position(self):
        """Update marker position based on current mouse position"""
        if not self.marker or not self.marker.is_active:
            return
            
        # Get current mouse position
        cursor_pos = self.canvas.mapFromGlobal(self.canvas.cursor().pos())
        map_point = self.canvas.mapSettings().mapToPixel().toMapCoordinates(
            cursor_pos.x(), cursor_pos.y()
        )
        
        self.marker.handle_mouse_move(map_point)
        
    def eventFilter(self, obj, event):
        """Filter events from canvas"""
        # Check if controller is enabled
        if not self.enabled:
            return False
            
        # Accept events from canvas or its viewport
        if not self.marker:
            return False
            
        # Check if event is from canvas or viewport
        if obj != self.canvas and (not hasattr(self.canvas, 'viewport') or obj != self.canvas.viewport()):
            return False
            
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_X:
                self.marker.toggle_active()
                # Start/stop timer based on active state
                if self.marker.is_active:
                    self.update_timer.start()
                else:
                    self.update_timer.stop()
                return True
            
        elif event.type() == event.MouseMove:
            if self.marker and self.marker.is_active:
                # Get map coordinates
                pos = event.pos()
                map_point = self.canvas.mapSettings().mapToPixel().toMapCoordinates(
                    int(pos.x()), int(pos.y())
                )
                self.marker.handle_mouse_move(map_point)
            return False  # Don't consume move events
            
        elif event.type() == event.MouseButtonPress:
            if event.button() == Qt.RightButton:
                # Check if marker is active
                if self.marker and self.marker.is_active:
                    QgsMessageLog.logMessage("Right click detected with active marker", "DualProfileViewer", Qgis.Info)
                    # Create perpendicular section at current marker position
                    self.marker.create_perpendicular_section()
                    return True
                else:
                    QgsMessageLog.logMessage(f"Right click but marker not active: marker={self.marker}, active={self.marker.is_active if self.marker else 'No marker'}", "DualProfileViewer", Qgis.Info)
                    
        return False
        
    def set_enabled(self, enabled):
        """Enable or disable the controller"""
        self.enabled = enabled
        if not enabled:
            self.update_timer.stop()
            if self.marker and self.marker.is_active:
                self.marker.is_active = False
                self.marker.update()
        QgsMessageLog.logMessage(f"Marker controller enabled: {enabled}", "DualProfileViewer", Qgis.Info)
    
    def cleanup(self):
        """Clean up the marker"""
        # Stop timer
        self.update_timer.stop()
        
        if self.marker:
            self.marker.set_visible(False)
            self.marker = None
        
        # Remove event filters
        self.canvas.removeEventFilter(self)
        if hasattr(self.canvas, 'viewport'):
            self.canvas.viewport().removeEventFilter(self)