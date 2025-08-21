# How to Fix Plugin Cache Issues in QGIS

The errors you're seeing suggest that QGIS is using a cached version of the Python files. Here's how to fix it:

## Method 1: Reload Plugin (Recommended)

1. Open QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Go to the **Installed** tab
4. Find "Dual Profile Viewer"
5. Uncheck the checkbox to disable it
6. Wait a moment, then check it again to re-enable
7. The plugin should reload with the latest code

## Method 2: Force Python Module Reload

1. Open the QGIS Python Console (Plugins → Python Console)
2. Run these commands:

```python
import sys
# Remove cached modules
modules_to_remove = [k for k in sys.modules.keys() if 'dual_profile_viewer' in k]
for module in modules_to_remove:
    del sys.modules[module]

# Reload the plugin
from qgis.utils import reloadPlugin
reloadPlugin('dual_profile_viewer')
```

## Method 3: Restart QGIS

1. Close QGIS completely
2. Make sure no QGIS processes are running
3. Start QGIS again
4. The plugin should load with the updated code

## Method 4: Clear Python Cache

1. Navigate to the plugin directory
2. Look for `__pycache__` folders
3. Delete all `__pycache__` folders
4. Restart QGIS

## Verify the Fix

After reloading, test single section drawing:
1. Click "➖ Single Line" button
2. Draw a single line
3. Click "📊 Create Profiles"
4. The profile should be created without errors

## If Issues Persist

If you still see the same errors after trying the above:

1. Check that the files were actually saved:
   - Open `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/dual_profile_viewer/compact_dual_profile_viewer.py`
   - Search for `single_mode` - you should find multiple occurrences
   - Check line ~1156 for the single mode check in update_statistics

2. Make sure you're editing the correct plugin installation:
   - In QGIS Python Console, run:
   ```python
   import dual_profile_viewer
   print(dual_profile_viewer.__file__)
   ```
   - This shows which plugin directory QGIS is actually using

3. Try manually applying the fix:
   - Open the QGIS Python Console
   - Run:
   ```python
   exec(open('/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/dual_profile_viewer/FIX_SINGLE_PROFILE_ISSUES.py').read())
   fix_single_profile_issues()
   ```

## About the Plotly Geological Viewer

The Plotly viewer requires the `plotly` package. To check if it's installed:

```python
try:
    import plotly
    print("Plotly is installed:", plotly.__version__)
except ImportError:
    print("Plotly is not installed")
```

If not installed, you can install it:
- On macOS: `pip3 install plotly`
- Or use the plugin's module installer if available

The Plotly viewer opens in your web browser, while PyVista opens within QGIS.