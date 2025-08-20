# -*- coding: utf-8 -*-
"""
Test script for 3D viewer functionality
Run this in QGIS Python Console after creating some profile sections
"""

print("=" * 60)
print("TESTING 3D GEOLOGICAL VIEWER")
print("=" * 60)

from qgis.utils import plugins
if 'dual_profile_viewer' not in plugins:
    print("✗ Plugin not loaded! Enable it first.")
else:
    plugin = plugins['dual_profile_viewer']
    print("✓ Plugin loaded")

print("\n1. PREPARATION:")
print("   - Create some profile sections first")
print("   - Click 'Add to Layer' to save them")
print("   - You should have layers with names containing 'section' or 'profile'")

print("\n2. TEST IMPORT SECTIONS:")
print("   a) Click the 3D button (🎲)")
print("   b) Choose 'Geological Section View (PyVista)'")
print("   c) In the right panel, find 'Import Sections'")
print("   d) Click 'Refresh Layers' - should list your section layers")
print("   e) Select a layer and click 'Import Selected Layer'")
print("   → You should see 3D walls appear")

print("\n3. TEST COLOR CHANGES:")
print("   a) After importing, check the 'Section Attributes' table")
print("   b) Click on a wall in the 3D view")
print("   c) The info label should show 'Selected: [section name]'")
print("   d) Click 'Choose Color' and pick a color")
print("   e) Click 'Apply Color'")
print("   → The selected wall should change color")

print("\n4. TEST INTERROGATION:")
print("   - Click on different walls in 3D view")
print("   - The attributes table should highlight the selected row")
print("   - Info label should update with section name")

print("\n5. VISUAL CONTROLS:")
print("   - Wall Thickness slider: Changes wall display thickness")
print("   - Vertical Scale slider: Exaggerates height")
print("   - Show Stratigraphic Layers: Shows elevation bands")
print("   - Show Intersections: Shows where walls cross")

print("\n6. REFERENCE PLANE:")
print("   - Check 'Show Reference Plane'")
print("   - Adjust elevation and opacity sliders")
print("   → A horizontal plane should appear at the specified elevation")

print("\nTROUBLESHOOTING:")
print("- If sections don't appear: Check QGIS log for errors")
print("- If colors don't change: Make sure you selected a section first")
print("- If interrogation doesn't work: PyVista picking might be disabled")

# Quick diagnostic
try:
    from qgis.core import QgsProject, QgsVectorLayer
    
    print("\nCURRENT VECTOR LAYERS:")
    layers = QgsProject.instance().mapLayers().values()
    section_layers = []
    for layer in layers:
        if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 1:  # Line
            if any(keyword in layer.name().lower() for keyword in ['section', 'profile', 'sezione']):
                section_layers.append(layer.name())
                print(f"  ✓ {layer.name()} - {layer.featureCount()} features")
    
    if not section_layers:
        print("  ✗ No section/profile layers found!")
        print("    Create profiles and use 'Add to Layer' first")
        
except Exception as e:
    print(f"\nError checking layers: {e}")

print("\n" + "=" * 60)