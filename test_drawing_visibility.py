# -*- coding: utf-8 -*-
"""
Test drawing visibility
Run this in QGIS Python Console to test the rubber band visibility
"""

print("TESTING DRAWING VISIBILITY")
print("=" * 50)

# Test manual rubber band creation
from qgis.gui import QgsRubberBand
from qgis.core import QgsWkbTypes, QgsPointXY
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt

canvas = iface.mapCanvas()

# Create a test rubber band
print("\n1. Creating test rubber band...")
test_band = QgsRubberBand(canvas, QgsWkbTypes.LineGeometry)
test_band.setColor(QColor(255, 0, 0, 255))
test_band.setWidth(5)

# Get center of current extent
extent = canvas.extent()
center = extent.center()
p1 = QgsPointXY(center.x() - 100, center.y())
p2 = QgsPointXY(center.x() + 100, center.y())

# Add points
test_band.addPoint(p1)
test_band.addPoint(p2)
test_band.show()

print("✓ Test rubber band created")
print("  You should see a RED horizontal line in the map center")
print("\nTo remove it, run:")
print("  canvas.scene().removeItem(test_band)")

print("\n2. TESTING PLUGIN DRAWING:")
print("   a) Select a DEM layer first")
print("   b) Click the 📏 Draw Lines button")
print("   c) Click once on the map")
print("   d) Move the mouse - you should see:")
print("      - Red line (profile A)")
print("      - Blue line (profile B)")
print("      - Gray dashed line (center)")

print("\n3. IF LINES DON'T APPEAR:")
print("   - The fixes have been applied to increase visibility:")
print("     • Increased line width (3 pixels)")
print("     • Full opacity (255)")
print("     • Added show() calls")
print("   - Try zooming in/out")
print("   - Check if your map canvas background makes lines hard to see")

print("\n4. ALTERNATIVE TEST:")
print("   If standard drawing doesn't work, try polygon drawing:")
print("   - Click ⬜ Draw Polygon")
print("   - Choose Rectangle mode")
print("   - This uses a different drawing mechanism")

# Check plugin status
from qgis.utils import plugins
if 'dual_profile_viewer' in plugins:
    plugin = plugins['dual_profile_viewer']
    if hasattr(plugin, 'viewer') and plugin.viewer:
        print("\n✓ Plugin viewer is active")
        if hasattr(plugin.viewer, 'map_tool'):
            print("✓ Map tool is available")
    else:
        print("\n⚠ Plugin viewer not active - open it from the toolbar")
else:
    print("\n✗ Plugin not loaded!")