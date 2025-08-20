#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify new features are working
"""

import sys
import os

# Add the plugin directory to path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

print("Testing Dual Profile Viewer Features\n")

# Test 1: Check polygon tool import
print("1. Testing polygon profile tool...")
try:
    from polygon_profile_tool import PolygonProfileTool
    print("✓ PolygonProfileTool imported successfully")
except ImportError as e:
    print(f"✗ Failed to import PolygonProfileTool: {e}")

# Test 2: Check geological viewer import
print("\n2. Testing geological viewer...")
try:
    from geological_3d_viewer import GeologicalSectionViewer
    print("✓ GeologicalSectionViewer imported successfully")
    
    # Check if methods exist
    methods = ['refresh_section_layers', 'import_section_layer', 'on_point_picked']
    for method in methods:
        if hasattr(GeologicalSectionViewer, method):
            print(f"  ✓ Method '{method}' exists")
        else:
            print(f"  ✗ Method '{method}' not found")
            
except ImportError as e:
    print(f"✗ Failed to import GeologicalSectionViewer: {e}")

# Test 3: Check layout generator
print("\n3. Testing layout generator...")
try:
    from layout_generator import LayoutGenerator
    print("✓ LayoutGenerator imported successfully")
except ImportError as e:
    print(f"✗ Failed to import LayoutGenerator: {e}")

# Test 4: Check compact viewer updates
print("\n4. Testing compact viewer features...")
try:
    from compact_dual_profile_viewer import CompactDualProfileViewer
    
    # Check for new methods
    new_methods = ['start_polygon_drawing', 'on_polygon_drawn', 
                   'create_multi_dem_layers', 'create_dem_section_layer']
    
    for method in new_methods:
        if hasattr(CompactDualProfileViewer, method):
            print(f"  ✓ Method '{method}' exists")
        else:
            print(f"  ✗ Method '{method}' not found")
            
except ImportError as e:
    print(f"✗ Failed to check CompactDualProfileViewer: {e}")

print("\nTest complete!")
print("\nIf all tests pass, the features should work in QGIS.")
print("If you still see issues, check the QGIS log panel for more details.")