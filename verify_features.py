# -*- coding: utf-8 -*-
"""
Run this script in QGIS Python Console to verify all features are working
Copy and paste this into the QGIS Python Console
"""

print("=" * 60)
print("VERIFYING DUAL PROFILE VIEWER FEATURES")
print("=" * 60)

# Check if plugin is loaded
from qgis.utils import plugins
if 'dual_profile_viewer' in plugins:
    print("✓ Plugin is loaded")
    plugin = plugins['dual_profile_viewer']
    
    # Check toolbar buttons
    print("\nTOOLBAR BUTTONS:")
    if hasattr(plugin, 'toolbar'):
        actions = plugin.toolbar.actions()
        for action in actions:
            print(f"  - {action.text()}")
    
    # Check if draw polygon button exists
    if hasattr(plugin, 'polygon_draw_btn'):
        print("\n✓ Polygon draw button exists")
    else:
        print("\n✗ Polygon draw button not found")
        
    # Check if layout button exists  
    if hasattr(plugin, 'layout_btn'):
        print("✓ Layout generator button exists")
    else:
        print("✗ Layout generator button not found")
        
else:
    print("✗ Plugin not loaded!")
    print("\nTo fix:")
    print("1. Go to Plugins → Manage and Install Plugins")
    print("2. Find 'Dual Profile Viewer'")
    print("3. Make sure it's enabled")
    print("4. If already enabled, disable and re-enable it")

print("\n" + "=" * 60)
print("QUICK FEATURE TEST:")
print("=" * 60)
print("\n1. TEST POLYGON DRAWING:")
print("   - Click the ⬜ (Draw Polygon) button in toolbar")
print("   - You should see a dialog with 3 options:")
print("     • Rectangle")
print("     • Polygon") 
print("     • Freehand")
print("   - Then a dialog asking for width in meters")

print("\n2. TEST 3D VIEW:")
print("   - Draw some profile lines")
print("   - Click the 🎲 (3D) button")
print("   - You should see ONLY 2 options:")
print("     • Geological Section View (PyVista)")
print("     • Geological Section View (Plotly)")
print("   - NO 'Standard 3D View' option")

print("\n3. TEST LAYOUT GENERATION:")
print("   - After creating profiles")
print("   - Click the 🖨️ (Generate Layout) button")
print("   - Should create an A3 layout in Layouts panel")

print("\n4. TEST MULTI-DEM LAYERS:")
print("   - Select multiple DEMs in the DEMs tab")
print("   - Draw profiles and click Add to Layer")
print("   - Should create separate layers for each DEM")

print("\nIf any feature doesn't work, check View → Panels → Log Messages")