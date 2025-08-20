"""
Test PyVista installation in QGIS
"""

print("Testing PyVista in QGIS...")

# Test 1: Import pyvista
try:
    import pyvista as pv
    print(f"✓ PyVista version: {pv.__version__}")
except Exception as e:
    print(f"✗ Error importing pyvista: {e}")
    print("\nTo install PyVista:")
    print("import subprocess, sys")
    print("subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', 'pyvista', 'pyvistaqt'])")

# Test 2: Import pyvistaqt
try:
    from pyvistaqt import QtInteractor
    print("✓ PyVistaQt available")
except Exception as e:
    print(f"✗ Error importing pyvistaqt: {e}")

# Test 3: Create simple plot
try:
    import pyvista as pv
    # Create a simple sphere
    sphere = pv.Sphere()
    print("✓ Created PyVista object")
    
    # Try to plot (might fail in headless environment)
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(sphere)
    print("✓ PyVista plotting works")
except Exception as e:
    print(f"✗ Error with PyVista plotting: {e}")

print("\nTesting complete!")

# Show current 3D options
print("\n3D Visualization Options:")
print("1. PyVista (advanced) - Requires pyvista and pyvistaqt")
print("2. Matplotlib (basic) - Always available")
print("3. Plotly (interactive) - Opens in browser, requires plotly")