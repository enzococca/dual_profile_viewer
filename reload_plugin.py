# -*- coding: utf-8 -*-
"""
Plugin Reload Utility
Force reload of all plugin modules to ensure changes take effect
"""

import sys
import importlib

def reload_dual_profile_viewer():
    """Force reload all dual profile viewer modules"""
    
    # List of modules to reload
    modules_to_reload = [
        'dual_profile_viewer.compact_dual_profile_viewer',
        'dual_profile_viewer.dual_profile_tool',
        'dual_profile_viewer.single_profile_tool',
        'dual_profile_viewer.polygon_profile_tool',
        'dual_profile_viewer.geological_3d_viewer',
        'dual_profile_viewer.plotly_geological_viewer',
        'dual_profile_viewer.profile_exporter',
        'dual_profile_viewer.vector_export_dialog',
        'dual_profile_viewer.multi_dem_widget',
        'dual_profile_viewer.layout_generator',
        'dual_profile_viewer.plot_generator',
        'dual_profile_viewer.wall_intersection_utils'
    ]
    
    # Remove modules from cache
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            del sys.modules[module_name]
    
    # Also remove the main module
    if 'dual_profile_viewer' in sys.modules:
        del sys.modules['dual_profile_viewer']
    
    print("Dual Profile Viewer modules cleared from cache. Plugin will reload on next use.")
    
    return True

# Run if executed directly
if __name__ == '__main__':
    reload_dual_profile_viewer()