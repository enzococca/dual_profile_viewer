"""
Direct test of 3D visualization with sample data
Run this in QGIS Python Console to test
"""

import numpy as np
from qgis.utils import iface

# Create sample profile data
distances = np.linspace(0, 100, 50)
elevations = 100 + 10 * np.sin(distances / 10) + np.random.normal(0, 0.5, 50)

# Format as expected by the viewer
profile_data = [(d, e, 0) for d, e in zip(distances, elevations)]

# Settings
settings = {
    'layer_count': 5,
    'cross_width': 50,
    'show_layers': True,
    'exploded_view': False,
    'show_grid': True,
    'colormap': 'terrain'
}

# Test matplotlib viewer directly
try:
    from dual_profile_viewer.simple_3d_viewer import Simple3DViewer
    viewer = Simple3DViewer(profile_data, settings, iface.mainWindow())
    viewer.show()
    print("✓ Matplotlib 3D viewer opened successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test if we can create a plot manually
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Simple test plot
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    z = np.cos(x)
    
    ax.plot(x, y, z)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    plt.show()
    print("✓ Direct matplotlib 3D plot works")
except Exception as e:
    print(f"✗ Matplotlib error: {e}")