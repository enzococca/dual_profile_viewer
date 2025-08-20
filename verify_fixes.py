# -*- coding: utf-8 -*-
"""
Quick verification script for the fixes
Run this in QGIS Python Console
"""

print("VERIFYING FIXES...")
print("=" * 50)

# Test 1: Check polygon tool fix
print("\n1. Testing polygon tool fix...")
try:
    import sys
    import os
    plugin_path = os.path.join(os.path.expanduser('~'), 
                              'Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/dual_profile_viewer')
    if plugin_path not in sys.path:
        sys.path.insert(0, plugin_path)
    
    from polygon_profile_tool import PolygonProfileTool
    
    # Check if the fix is in place
    import inspect
    source = inspect.getsource(PolygonProfileTool.show_rectangle_preview)
    if 'if rect_points:' in source:
        print("✓ Polygon tool IndexError fix is in place")
    else:
        print("✗ Polygon tool fix not found")
except Exception as e:
    print(f"✗ Error checking polygon tool: {e}")

# Test 2: Check layout generator fix
print("\n2. Testing layout generator fix...")
try:
    from layout_generator import LayoutGenerator
    
    # Check if the fix is in place
    source = inspect.getsource(LayoutGenerator.add_statistics_table)
    if 'profile_a_label' in source and 'profile_b_label' in source:
        print("✓ Layout generator SyntaxError fix is in place")
    else:
        print("✗ Layout generator fix not found")
except SyntaxError as e:
    print(f"✗ SyntaxError still present: {e}")
except Exception as e:
    print(f"✗ Error checking layout generator: {e}")

print("\n" + "=" * 50)
print("TESTING RECOMMENDATIONS:")
print("\n1. For Polygon Drawing:")
print("   - Click the ⬜ button")
print("   - Choose Rectangle mode")
print("   - Click once and move mouse - should show preview without errors")
print("   - Click second time to complete rectangle")

print("\n2. For Layout Generation:")
print("   - Create some profiles first")
print("   - Click the 🖨️ button")
print("   - Should generate layout without SyntaxError")

print("\nIf errors persist, reload the plugin:")
print("Plugins → Reload Plugin → Dual Profile Viewer")