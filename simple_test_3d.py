"""
Simple 3D test viewer that always shows sample data
"""

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt


class SimpleTest3DViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Test Visualization")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.create_test_plot()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        
    def create_test_plot(self):
        self.figure.clear()
        
        # Create 3D subplot
        ax = self.figure.add_subplot(111, projection='3d')
        
        # Create test data - two intersecting profiles
        # Profile 1 along X axis
        x1 = np.linspace(-50, 50, 100)
        y1 = np.zeros_like(x1)
        z1 = 100 + 10 * np.sin(x1 / 10) + np.random.normal(0, 0.5, 100)
        
        # Profile 2 along Y axis
        x2 = np.zeros_like(x1)
        y2 = np.linspace(-50, 50, 100)
        z2 = 100 + 5 * np.cos(y2 / 10) + np.random.normal(0, 0.5, 100)
        
        # Create surfaces
        # Surface 1
        Y1, X1 = np.meshgrid(np.linspace(-10, 10, 10), x1)
        Z1 = np.tile(z1, (10, 1)).T
        
        # Surface 2
        X2, Y2 = np.meshgrid(np.linspace(-10, 10, 10), y2)
        Z2 = np.tile(z2, (10, 1)).T
        
        # Plot surfaces
        surf1 = ax.plot_surface(X1, Y1, Z1, cmap='terrain', alpha=0.8)
        surf2 = ax.plot_surface(X2, Y2, Z2, cmap='viridis', alpha=0.8)
        
        # Plot profile lines
        ax.plot(x1, y1, z1, 'r-', linewidth=3, label='Profile 1')
        ax.plot(x2, y2, z2, 'b-', linewidth=3, label='Profile 2')
        
        # Add intersection point
        ax.scatter([0], [0], [100], color='yellow', s=100, label='Intersection')
        
        # Set labels and title
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Elevation (m)')
        ax.set_title('Test Cross-Section 3D Visualization')
        
        # Add legend
        ax.legend()
        
        # Set view angle
        ax.view_init(elev=30, azim=45)
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Draw
        self.canvas.draw()


# Function to show test viewer
def show_test_3d_viewer(parent=None):
    viewer = SimpleTest3DViewer(parent)
    viewer.exec_()
    return viewer