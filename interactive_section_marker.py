# -*- coding: utf-8 -*-
"""
Interactive Section Marker
Handles interactive marker on section line that syncs with graph
"""

from qgis.PyQt.QtCore import Qt, QObject, pyqtSignal, QPointF, QTimer, QRectF
from qgis.PyQt.QtGui import QColor, QPen, QBrush, QKeyEvent
from qgis.PyQt.QtWidgets import QGraphicsEllipseItem, QInputDialog, QMessageBox
from qgis.core import (
    QgsPointXY, QgsGeometry, QgsVectorLayer, QgsFeature,
    QgsProject, QgsCoordinateTransform, QgsDistanceArea,
    QgsWkbTypes
)
from qgis.gui import QgsMapCanvasItem, QgsRubberBand
import math


class InteractiveSectionMarker(QgsMapCanvasItem, QObject):
    """Interactive marker that moves along section line"""
    
    # Signals
    position_changed = pyqtSignal(float)  # Emits normalized position (0-1)
    perpendicular_requested = pyqtSignal(QgsPointXY, float, float)  # point, angle, length
    
    def __init__(self, canvas, section_line):
        QgsMapCanvasItem.__init__(self, canvas)
        QObject.__init__(self)
        
        self.canvas = canvas
        # Convert to QgsGeometry if it's a list
        if isinstance(section_line, list):
            self.section_line = QgsGeometry.fromPolylineXY(section_line)
        else:
            self.section_line = section_line
        self.normalized_position = 0.0  # Position along line (0-1)
        self.is_dragging = False
        self.marker_radius = 12  # Increased for better visibility
        
        # Visual properties
        self.normal_color = QColor(255, 0, 0, 200)
        self.hover_color = QColor(255, 100, 100, 255)
        self.current_color = self.normal_color
        
        # Key press tracking
        self.x_pressed = False
        self.right_click_pos = None
        
        # Create rubber band for perpendicular preview
        self.perpendicular_preview = QgsRubberBand(canvas, QgsWkbTypes.LineGeometry)
        self.perpendicular_preview.setColor(QColor(0, 255, 0, 150))
        self.perpendicular_preview.setWidth(2)
        
        # Install event filter on canvas to catch key events
        self.canvas.installEventFilter(self)
        
        self.update_position(0.0)
        
    def update_section_line(self, new_line):
        """Update the section line geometry"""
        # Convert to QgsGeometry if it's a list
        if isinstance(new_line, list):
            self.section_line = QgsGeometry.fromPolylineXY(new_line)
        else:
            self.section_line = new_line
        self.update_position(self.normalized_position)
        
    def update_position(self, normalized_pos):
        """Update marker position along line (0-1)"""
        self.normalized_position = max(0.0, min(1.0, normalized_pos))
        
        # Calculate actual position on line
        if self.section_line and not self.section_line.isEmpty():
            length = self.section_line.length()
            distance = length * self.normalized_position
            
            # Get point at distance
            point = self.section_line.interpolate(distance)
            if point and not point.isEmpty():
                # Convert to canvas coordinates
                canvas_point = self.canvas.mapSettings().mapToPixel().transform(point.asPoint())
                self.setPos(canvas_point.x(), canvas_point.y())
                self.show()
                self.update()
                
                # Debug log
                from qgis.core import QgsMessageLog, Qgis
                QgsMessageLog.logMessage(
                    f"Marker position updated: {point.asPoint().x():.2f}, {point.asPoint().y():.2f} -> Canvas: {canvas_point.x():.2f}, {canvas_point.y():.2f}", 
                    "DualProfileViewer", Qgis.Info
                )
                
    def get_current_point(self):
        """Get current point on section line"""
        if self.section_line and not self.section_line.isEmpty():
            length = self.section_line.length()
            distance = length * self.normalized_position
            point = self.section_line.interpolate(distance)
            if point and not point.isEmpty():
                return point.asPoint()
        return None
        
    def get_perpendicular_angle(self):
        """Get angle perpendicular to section at current position"""
        if self.section_line and not self.section_line.isEmpty():
            # Get a small segment around current position
            length = self.section_line.length()
            distance = length * self.normalized_position
            
            # Get points slightly before and after
            delta = min(1.0, length * 0.01)
            p1 = self.section_line.interpolate(max(0, distance - delta))
            p2 = self.section_line.interpolate(min(length, distance + delta))
            
            if p1 and p2 and not p1.isEmpty() and not p2.isEmpty():
                # Calculate angle
                dx = p2.asPoint().x() - p1.asPoint().x()
                dy = p2.asPoint().y() - p1.asPoint().y()
                angle = math.atan2(dy, dx)
                
                # Perpendicular angle (add 90 degrees)
                return angle + math.pi / 2
        return 0
        
    def show_perpendicular_preview(self, length):
        """Show preview of perpendicular section"""
        point = self.get_current_point()
        if point:
            angle = self.get_perpendicular_angle()
            
            # Calculate end points of perpendicular line
            half_length = length / 2
            dx = math.cos(angle) * half_length
            dy = math.sin(angle) * half_length
            
            start_point = QgsPointXY(point.x() - dx, point.y() - dy)
            end_point = QgsPointXY(point.x() + dx, point.y() + dy)
            
            # Update preview rubber band
            self.perpendicular_preview.reset(False)
            self.perpendicular_preview.addPoint(start_point)
            self.perpendicular_preview.addPoint(end_point)
            self.perpendicular_preview.show()
            
    def hide_perpendicular_preview(self):
        """Hide perpendicular preview"""
        self.perpendicular_preview.hide()
        self.perpendicular_preview.reset()
        
    def paint(self, painter, option, widget):
        """Paint the marker"""
        try:
            if not self.get_current_point():
                return
                
            # Draw marker with multiple rings for visibility
            painter.setRenderHint(painter.Antialiasing)
            
            # Outer ring (shadow effect)
            painter.setPen(QPen(QColor(0, 0, 0, 100), 4))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(0, 0), self.marker_radius + 2, self.marker_radius + 2)
            
            # Main circle
            painter.setPen(QPen(self.current_color, 3))
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.drawEllipse(QPointF(0, 0), self.marker_radius, self.marker_radius)
            
            # Inner ring
            painter.setPen(QPen(self.current_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(0, 0), self.marker_radius - 4, self.marker_radius - 4)
            
            # Center dot
            painter.setBrush(QBrush(self.current_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(0, 0), 4, 4)
        except Exception as e:
            # Silently fail painting if there's an error
            pass
        
    def boundingRect(self):
        """Return bounding rectangle"""
        return QRectF(-self.marker_radius - 2, -self.marker_radius - 2,
                     2 * self.marker_radius + 4, 2 * self.marker_radius + 4)
        
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.current_color = self.hover_color
            self.update()
        elif event.button() == Qt.RightButton:
            self.right_click_pos = event.pos()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self.is_dragging and self.section_line:
            # Convert mouse position to map coordinates
            point = self.canvas.mapSettings().mapToPixel().toMapCoordinates(int(event.pos().x()), int(event.pos().y()))
            
            # Find closest point on line
            closest = self.section_line.closestSegmentWithContext(QgsPointXY(point))
            if closest[0] >= 0:  # Valid result
                # Calculate normalized position
                length = self.section_line.length()
                if length > 0:
                    # Get distance to start of line
                    start_point = self.section_line.asPolyline()[0]
                    closest_point = QgsPointXY(closest[1], closest[2])
                    
                    # Calculate distance along line
                    # This is approximate but works well for most cases
                    distance = math.sqrt((closest_point.x() - start_point.x())**2 + 
                                       (closest_point.y() - start_point.y())**2)
                    
                    # More accurate: use interpolate to find exact position
                    min_dist = float('inf')
                    best_pos = 0
                    
                    # Sample points along line to find closest
                    for i in range(101):
                        test_pos = i / 100.0
                        test_dist = length * test_pos
                        test_point = self.section_line.interpolate(test_dist)
                        if test_point and not test_point.isEmpty():
                            dist = closest_point.distance(test_point.asPoint())
                            if dist < min_dist:
                                min_dist = dist
                                best_pos = test_pos
                    
                    self.normalized_position = best_pos
                    self.update_position(self.normalized_position)
                    self.position_changed.emit(self.normalized_position)
                    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.current_color = self.normal_color
            self.update()
        elif event.button() == Qt.RightButton and self.x_pressed:
            # Request perpendicular section
            self.request_perpendicular_section()
            
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key_X:
            self.x_pressed = True
            
    def keyReleaseEvent(self, event):
        """Handle key release"""
        if event.key() == Qt.Key_X:
            self.x_pressed = False
            self.hide_perpendicular_preview()
            
    def request_perpendicular_section(self):
        """Request creation of perpendicular section"""
        point = self.get_current_point()
        if not point:
            return
            
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
            angle = self.get_perpendicular_angle()
            self.perpendicular_requested.emit(point, angle, length)
            
    def set_visible(self, visible):
        """Set marker visibility"""
        if visible:
            self.show()
        else:
            self.hide()
            self.hide_perpendicular_preview()
            
    def update_to_closest_point(self, point):
        """Update marker to closest point on line"""
        if not self.section_line or self.section_line.isEmpty():
            return
            
        # Find normalized position along line
        length = self.section_line.length()
        if length > 0:
            # Sample points to find closest position
            min_dist = float('inf')
            best_pos = 0
            
            for i in range(101):
                test_pos = i / 100.0
                test_dist = length * test_pos
                test_point = self.section_line.interpolate(test_dist)
                if test_point and not test_point.isEmpty():
                    dist = point.distance(test_point.asPoint())
                    if dist < min_dist:
                        min_dist = dist
                        best_pos = test_pos
            
            self.update_position(best_pos)
            self.position_changed.emit(best_pos)
            
    def eventFilter(self, obj, event):
        """Event filter to catch key events on canvas"""
        if obj == self.canvas:
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_X:
                    self.x_pressed = True
                    return True
            elif event.type() == event.KeyRelease:
                if event.key() == Qt.Key_X:
                    self.x_pressed = False
                    self.hide_perpendicular_preview()
                    return True
            elif event.type() == event.MouseButtonPress:
                if event.button() == Qt.RightButton and self.x_pressed:
                    # Convert to map coordinates
                    canvas_pos = self.canvas.mouseLastXY()
                    map_point = self.canvas.mapSettings().mapToPixel().toMapCoordinates(canvas_pos.x(), canvas_pos.y())
                    
                    # Find closest point on line
                    closest = self.section_line.closestSegmentWithContext(map_point)
                    if closest[0] >= 0:
                        closest_point = QgsPointXY(closest[1], closest[2])
                        # Update marker position to closest point
                        self.update_to_closest_point(closest_point)
                        # Request perpendicular section
                        self.request_perpendicular_section()
                        return True
        
        return False


class GraphInteractionHandler(QObject):
    """Handles interaction between graph and map marker"""
    
    marker_position_requested = pyqtSignal(float)  # Request marker position update
    
    def __init__(self, plot_widget):
        super().__init__()
        self.plot_widget = plot_widget
        self.is_connected = False
        
    def connect_plotly_interaction(self):
        """Connect to Plotly graph interactions"""
        if hasattr(self.plot_widget, 'page'):
            # Inject JavaScript for interaction
            js_code = """
            if (window.Plotly) {
                var plot = document.getElementsByClassName('plotly')[0];
                if (plot) {
                    plot.on('plotly_hover', function(data) {
                        var point = data.points[0];
                        if (point && point.x !== undefined) {
                            // Calculate normalized position (0-1)
                            var xRange = plot.layout.xaxis.range;
                            var normalizedPos = (point.x - xRange[0]) / (xRange[1] - xRange[0]);
                            
                            // Send to Qt
                            if (window.qt && window.qt.webChannelTransport) {
                                window.qt.webChannelTransport.send(JSON.stringify({
                                    'type': 'hover',
                                    'position': normalizedPos
                                }));
                            }
                        }
                    });
                    
                    plot.on('plotly_click', function(data) {
                        var point = data.points[0];
                        if (point && point.x !== undefined) {
                            var xRange = plot.layout.xaxis.range;
                            var normalizedPos = (point.x - xRange[0]) / (xRange[1] - xRange[0]);
                            
                            if (window.qt && window.qt.webChannelTransport) {
                                window.qt.webChannelTransport.send(JSON.stringify({
                                    'type': 'click',
                                    'position': normalizedPos
                                }));
                            }
                        }
                    });
                }
            }
            """
            
            self.plot_widget.page().runJavaScript(js_code)
            self.is_connected = True
            
    def update_graph_marker(self, normalized_pos):
        """Update marker position on graph"""
        if hasattr(self.plot_widget, 'page') and self.is_connected:
            js_code = f"""
            if (window.Plotly) {{
                var plot = document.getElementsByClassName('plotly')[0];
                if (plot && plot.layout) {{
                    var xRange = plot.layout.xaxis.range;
                    var xPos = xRange[0] + (xRange[1] - xRange[0]) * {normalized_pos};
                    
                    // Add or update vertical line
                    var shapes = plot.layout.shapes || [];
                    var markerShape = {{
                        type: 'line',
                        x0: xPos,
                        x1: xPos,
                        y0: 0,
                        y1: 1,
                        yref: 'paper',
                        line: {{
                            color: 'red',
                            width: 2,
                            dash: 'dot'
                        }}
                    }};
                    
                    // Update shapes
                    shapes = shapes.filter(s => s.line && s.line.color !== 'red');
                    shapes.push(markerShape);
                    
                    Plotly.relayout(plot, {{'shapes': shapes}});
                }}
            }}
            """
            
            self.plot_widget.page().runJavaScript(js_code)