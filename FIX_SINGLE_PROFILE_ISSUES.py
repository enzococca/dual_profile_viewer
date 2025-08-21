# -*- coding: utf-8 -*-
"""
Fix for Single Profile Issues
Run this script in QGIS Python Console to fix the issues
"""

def fix_single_profile_issues():
    """Apply fixes to the compact dual profile viewer"""
    
    # Import necessary modules
    import os
    import sys
    from qgis.core import QgsMessageLog, Qgis
    
    # Get plugin path
    plugin_path = os.path.dirname(__file__)
    file_path = os.path.join(plugin_path, 'compact_dual_profile_viewer.py')
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        QgsMessageLog.logMessage(f"Error reading file: {str(e)}", 'DualProfileViewer', Qgis.Critical)
        return False
    
    # Fix 1: Update statistics to handle None properly
    # Find the update_statistics method and ensure it checks for None
    old_stats = """diff = profile1['elevations'] - profile2['elevations']"""
    new_stats = """if profile2 is not None:
                diff = profile1['elevations'] - profile2['elevations']
            else:
                diff = np.array([])"""
    
    if old_stats in content and new_stats not in content:
        content = content.replace(old_stats, new_stats)
        QgsMessageLog.logMessage("Fixed statistics diff calculation", 'DualProfileViewer', Qgis.Info)
    
    # Fix 2: Ensure plotly figure handles single mode in differences
    old_plotly_diff = """# Top right - Elevation differences
            diff = profile1['elevations'] - profile2['elevations']"""
    new_plotly_diff = """# Top right - Elevation differences
            if not single_mode and profile2 is not None:
                diff = profile1['elevations'] - profile2['elevations']
            else:
                diff = np.zeros_like(profile1['elevations'])"""
    
    if old_plotly_diff in content:
        content = content.replace(old_plotly_diff, new_plotly_diff)
        QgsMessageLog.logMessage("Fixed plotly diff calculation", 'DualProfileViewer', Qgis.Info)
    
    # Fix 3: Ensure profile2 is checked before plotting in matplotlib
    # This should already be fixed by the single_mode check
    
    # Write the fixed content back
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        QgsMessageLog.logMessage("Successfully applied fixes to compact_dual_profile_viewer.py", 'DualProfileViewer', Qgis.Info)
    except Exception as e:
        QgsMessageLog.logMessage(f"Error writing file: {str(e)}", 'DualProfileViewer', Qgis.Critical)
        return False
    
    # Force reload of modules
    modules_to_reload = [
        'dual_profile_viewer.compact_dual_profile_viewer',
        'dual_profile_viewer.plotly_geological_viewer',
        'dual_profile_viewer'
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            del sys.modules[module_name]
    
    QgsMessageLog.logMessage("Cleared module cache. Please reload the plugin.", 'DualProfileViewer', Qgis.Info)
    
    return True

# To use this fix:
# 1. Open QGIS Python Console
# 2. Run: exec(open('/path/to/FIX_SINGLE_PROFILE_ISSUES.py').read())
# 3. Then: fix_single_profile_issues()
# 4. Reload the plugin from Plugin Manager

if __name__ == '__main__':
    print("To fix the issues:")
    print("1. Run fix_single_profile_issues() in QGIS Python Console")
    print("2. Reload the Dual Profile Viewer plugin")