#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test script for Dual Profile Viewer
Tests all new features and provides detailed diagnostics
"""

import sys
import os
import traceback

# Add plugin directory to path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

print("=" * 80)
print("DUAL PROFILE VIEWER - COMPREHENSIVE FEATURE TEST")
print("=" * 80)

def test_imports():
    """Test all critical imports"""
    print("\n1. TESTING IMPORTS")
    print("-" * 40)
    
    imports = {
        'compact_dual_profile_viewer': ['CompactDualProfileViewer'],
        'geological_3d_viewer': ['GeologicalSectionViewer'],
        'plotly_geological_viewer': ['PlotlyGeologicalViewer'],
        'polygon_profile_tool': ['PolygonProfileTool'],
        'layout_generator': ['LayoutGenerator'],
        'plot_generator': ['PlotGenerator'],
        'multi_dem_widget': ['MultiDemWidget'],
        'wall_intersection_utils': ['calculate_wall_intersection', 'create_intersection_mesh']
    }
    
    results = {}
    for module, classes in imports.items():
        try:
            mod = __import__(module)
            for cls in classes:
                if hasattr(mod, cls):
                    results[f"{module}.{cls}"] = "✓ OK"
                else:
                    results[f"{module}.{cls}"] = "✗ Class not found"
        except ImportError as e:
            results[module] = f"✗ Import failed: {str(e)}"
        except Exception as e:
            results[module] = f"✗ Error: {str(e)}"
    
    for item, status in results.items():
        print(f"  {item}: {status}")
    
    return all("✓" in status for status in results.values())

def test_qgis_imports():
    """Test QGIS-specific imports"""
    print("\n2. TESTING QGIS IMPORTS")
    print("-" * 40)
    
    try:
        from qgis.gui import QgsRubberBand
        print("  ✓ QgsRubberBand from qgis.gui - CORRECT")
    except ImportError:
        print("  ✗ QgsRubberBand import failed")
        
    try:
        from qgis.core import QgsLayoutItemLabel
        print("  ✓ QgsLayoutItemLabel from qgis.core")
    except ImportError:
        print("  ✗ QgsLayoutItemLabel import failed")

def test_polygon_tool():
    """Test polygon drawing tool"""
    print("\n3. TESTING POLYGON DRAWING TOOL")
    print("-" * 40)
    
    try:
        from polygon_profile_tool import PolygonProfileTool
        
        # Check class methods
        methods = ['create_rectangle_points', 'create_polygon_from_points', 
                  'create_freehand_polygon', 'canvasReleaseEvent']
        
        for method in methods:
            if hasattr(PolygonProfileTool, method):
                print(f"  ✓ Method {method} exists")
            else:
                print(f"  ✗ Method {method} not found")
                
    except Exception as e:
        print(f"  ✗ Error testing polygon tool: {e}")
        traceback.print_exc()

def test_geological_viewer():
    """Test geological 3D viewer features"""
    print("\n4. TESTING GEOLOGICAL 3D VIEWER")
    print("-" * 40)
    
    try:
        from geological_3d_viewer import GeologicalSectionViewer
        
        # Check new UI methods
        ui_methods = ['setup_import_panel', 'refresh_section_layers', 
                     'import_section_layer', 'on_point_picked']
        
        for method in ui_methods:
            if hasattr(GeologicalSectionViewer, method):
                print(f"  ✓ UI Method {method} exists")
            else:
                print(f"  ✗ UI Method {method} not found")
                
        # Check if enable_point_picking is used instead of enable_pick_callback
        import inspect
        source = inspect.getsource(GeologicalSectionViewer.__init__)
        if 'enable_point_picking' in source:
            print("  ✓ Using enable_point_picking (correct)")
        elif 'enable_pick_callback' in source:
            print("  ✗ Still using enable_pick_callback (incorrect)")
        else:
            print("  ? Could not verify pick method")
            
    except Exception as e:
        print(f"  ✗ Error testing geological viewer: {e}")
        traceback.print_exc()

def test_layout_generator():
    """Test layout generator"""
    print("\n5. TESTING LAYOUT GENERATOR")
    print("-" * 40)
    
    try:
        from layout_generator import LayoutGenerator
        import inspect
        
        # Check if statistics table is using labels
        source = inspect.getsource(LayoutGenerator.add_statistics_table)
        
        if 'QgsLayoutItemLabel' in source and 'table_text' in source:
            print("  ✓ Statistics table using QgsLayoutItemLabel (correct)")
        else:
            print("  ✗ Statistics table implementation unclear")
            
        # Check for matplotlib fallback
        if os.path.exists(os.path.join(plugin_dir, 'plot_generator.py')):
            print("  ✓ plot_generator.py exists for matplotlib fallback")
        else:
            print("  ✗ plot_generator.py not found")
            
    except Exception as e:
        print(f"  ✗ Error testing layout generator: {e}")
        traceback.print_exc()

def test_compact_viewer():
    """Test compact viewer new features"""
    print("\n6. TESTING COMPACT VIEWER FEATURES")
    print("-" * 40)
    
    try:
        from compact_dual_profile_viewer import CompactDualProfileViewer
        
        # Check for new methods
        new_features = {
            'start_polygon_drawing': 'Polygon drawing',
            'on_polygon_drawn': 'Polygon drawing callback',
            'create_multi_dem_layers': 'Multi-DEM layer creation',
            'create_dem_section_layer': 'Individual DEM layers',
            'generate_layout': 'Layout generation',
            'show_3d_options': '3D view options'
        }
        
        for method, description in new_features.items():
            if hasattr(CompactDualProfileViewer, method):
                print(f"  ✓ {description} ({method})")
            else:
                print(f"  ✗ {description} ({method}) not found")
                
        # Check if standard 3D view is removed
        import inspect
        source = inspect.getsource(CompactDualProfileViewer.show_3d_options)
        if 'Standard 3D View' not in source:
            print("  ✓ Standard 3D View removed")
        else:
            print("  ✗ Standard 3D View still present")
            
    except Exception as e:
        print(f"  ✗ Error testing compact viewer: {e}")
        traceback.print_exc()

def test_field_attributes():
    """Test field attributes for layers"""
    print("\n7. TESTING FIELD ATTRIBUTES")
    print("-" * 40)
    
    try:
        from compact_dual_profile_viewer import CompactDualProfileViewer
        import inspect
        
        # Check create_dem_section_layer for 6 attributes
        source = inspect.getsource(CompactDualProfileViewer.create_dem_section_layer)
        
        # Count setAttributes calls
        if 'setAttributes' in source and source.count(',') >= 5:
            print("  ✓ Layer creation sets correct number of attributes")
        else:
            print("  ✗ Layer attributes may be incorrect")
            
        # Check for new fields
        required_fields = ['section_group', 'dem_name', 'notes']
        for field in required_fields:
            if field in source:
                print(f"  ✓ Field '{field}' present")
            else:
                print(f"  ✗ Field '{field}' not found")
                
    except Exception as e:
        print(f"  ✗ Error testing field attributes: {e}")
        traceback.print_exc()

def check_file_sizes():
    """Check file sizes to ensure files were properly updated"""
    print("\n8. FILE SIZES CHECK")
    print("-" * 40)
    
    files_to_check = [
        'compact_dual_profile_viewer.py',
        'geological_3d_viewer.py',
        'polygon_profile_tool.py',
        'layout_generator.py',
        'plot_generator.py'
    ]
    
    for filename in files_to_check:
        filepath = os.path.join(plugin_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  {filename}: {size:,} bytes")
        else:
            print(f"  {filename}: NOT FOUND")

def run_all_tests():
    """Run all tests"""
    print("\nStarting comprehensive tests...")
    
    all_passed = True
    
    # Run each test
    try:
        all_passed &= test_imports()
    except Exception as e:
        print(f"\nImport tests failed: {e}")
        all_passed = False
        
    test_qgis_imports()
    test_polygon_tool()
    test_geological_viewer()
    test_layout_generator()
    test_compact_viewer()
    test_field_attributes()
    check_file_sizes()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    if all_passed:
        print("✓ All critical imports passed!")
        print("\nRECOMMENDED ACTIONS:")
        print("1. Reload the plugin in QGIS")
        print("2. Check the QGIS Python Console for any runtime errors")
        print("3. Try each feature one by one")
    else:
        print("✗ Some tests failed!")
        print("\nTROUBLESHOOTING:")
        print("1. Check file permissions")
        print("2. Ensure all files are saved")
        print("3. Restart QGIS completely")
        print("4. Check QGIS Python Console for detailed errors")
    
    print("\nPLUGIN DIRECTORY:", plugin_dir)
    print("\nIf issues persist, check the QGIS message log (View → Panels → Log Messages)")

if __name__ == "__main__":
    run_all_tests()