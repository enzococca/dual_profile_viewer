"""
Test script for 3D visualization
Run this in QGIS Python console to test the 3D viewer
"""

# Test if matplotlib is available
try:
    import matplotlib
    print("✓ Matplotlib is available")
except ImportError:
    print("✗ Matplotlib is NOT available")

# Test if numpy is available
try:
    import numpy as np
    print("✓ NumPy is available")
except ImportError:
    print("✗ NumPy is NOT available")

# Test the simple 3D viewer
try:
    from dual_profile_viewer.simple_3d_viewer import Simple3DViewer
    
    # Create test data
    distances = np.linspace(0, 100, 50)
    elevations = 100 + 10 * np.sin(distances / 10) + np.random.normal(0, 0.5, 50)
    profile_data = [(d, e, 0) for d, e in zip(distances, elevations)]
    
    # Test settings
    settings = {
        'layer_count': 10,
        'cross_width': 50,
        'show_layers': True,
        'exploded_view': False,
        'show_grid': True,
        'colormap': 'terrain'
    }
    
    # Create and show viewer
    viewer = Simple3DViewer(profile_data, settings)
    viewer.show()
    print("✓ 3D viewer created successfully!")
    
except Exception as e:
    print(f"✗ Error creating 3D viewer: {e}")
    import traceback
    traceback.print_exc()