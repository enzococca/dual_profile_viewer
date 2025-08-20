#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test if the compact viewer loads correctly
"""

import sys
import os

# Add the plugin directory to path
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

try:
    from compact_dual_profile_viewer import CompactDualProfileViewer
    print("✓ CompactDualProfileViewer imported successfully")
    
    from dual_profile_dock import DualProfileDock
    print("✓ DualProfileDock imported successfully")
    
    # Test if all required modules can be imported
    from PyQt5 import QtWidgets, QtCore
    print("✓ PyQt5 modules imported successfully")
    
    # Check if the draw function exists
    if hasattr(CompactDualProfileViewer, 'start_drawing'):
        print("✓ start_drawing method exists")
    else:
        print("✗ start_drawing method not found")
    
    print("\nAll imports successful! The compact viewer should load correctly.")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")