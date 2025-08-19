"""
Test matplotlib in QGIS
"""

print("Testing matplotlib in QGIS...")

# Test 1: Import matplotlib
try:
    import matplotlib
    print(f"✓ Matplotlib version: {matplotlib.__version__}")
    print(f"✓ Matplotlib backend: {matplotlib.get_backend()}")
except Exception as e:
    print(f"✗ Error importing matplotlib: {e}")

# Test 2: Set backend
try:
    matplotlib.use('Qt5Agg')
    print("✓ Set Qt5Agg backend")
except Exception as e:
    print(f"✗ Error setting backend: {e}")

# Test 3: Import pyplot
try:
    import matplotlib.pyplot as plt
    print("✓ Imported pyplot")
except Exception as e:
    print(f"✗ Error importing pyplot: {e}")

# Test 4: Import 3D
try:
    from mpl_toolkits.mplot3d import Axes3D
    print("✓ Imported 3D toolkit")
except Exception as e:
    print(f"✗ Error importing 3D: {e}")

# Test 5: Create simple figure
try:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot([1, 2, 3], [1, 2, 3], [1, 2, 3])
    print("✓ Created 3D figure")
    plt.close(fig)
except Exception as e:
    print(f"✗ Error creating figure: {e}")

# Test 6: Qt integration
try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    print("✓ Qt5 backend available")
except Exception as e:
    print(f"✗ Error with Qt5 backend: {e}")

print("\nTesting complete!")