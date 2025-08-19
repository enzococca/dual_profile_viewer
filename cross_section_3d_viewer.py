"""
Cross-section 3D viewer using matplotlib for multiple intersecting profiles
"""

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from qgis.core import QgsMessageLog, Qgis


class CrossSection3DViewer(QDialog):
    def __init__(self, profile_data_list, settings, parent=None):
        super().__init__(parent)
        self.profile_data_list = profile_data_list
        self.settings = settings
        self.setWindowTitle("3D Cross-Section Visualization")
        self.setMinimumSize(900, 700)
        self.init_ui()
        self.create_3d_plot()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Info label
        self.info_label = QLabel("Drag to rotate • Scroll to zoom • Click points for coordinates")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.rotate_button = QPushButton("Auto Rotate")
        self.rotate_button.setCheckable(True)
        self.rotate_button.clicked.connect(self.toggle_rotation)
        button_layout.addWidget(self.rotate_button)
        
        self.reset_button = QPushButton("Reset View")
        self.reset_button.clicked.connect(self.reset_view)
        button_layout.addWidget(self.reset_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.rotation_timer = None
        
    def create_3d_plot(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        if not self.profile_data_list:
            self.ax.text(0.5, 0.5, 0.5, 'No profile data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        QgsMessageLog.logMessage(f"Creating cross-section with {len(self.profile_data_list)} profiles", 
                                "DualProfileViewer", Qgis.Info)
        
        colors = ['red', 'blue', 'green', 'orange', 'purple']
        cross_width = self.settings.get('cross_width', 100)
        n_cross = 10
        
        # Process each profile
        for idx, profile_data in enumerate(self.profile_data_list):
            if not profile_data:
                continue
                
            # Convert to array
            if isinstance(profile_data, list):
                profile_array = np.array(profile_data)
            else:
                profile_array = profile_data
                
            # Handle different shapes
            if len(profile_array.shape) == 3:
                profile_array = profile_array[0]
                
            if len(profile_array.shape) != 2 or profile_array.shape[1] < 2:
                QgsMessageLog.logMessage(f"Skipping invalid profile {idx}", "DualProfileViewer", Qgis.Warning)
                continue
                
            distances = profile_array[:, 0]
            elevations = profile_array[:, 1]
            color = colors[idx % len(colors)]
            
            # Create cross-section positioning
            if idx == 0:
                # First profile along X axis
                x = distances
                y = np.zeros_like(distances)
                
                # Create surface
                Y_mesh = np.linspace(-cross_width/2, cross_width/2, n_cross)
                X_mesh, Y_mesh = np.meshgrid(x, Y_mesh)
                Z_mesh = np.tile(elevations, (n_cross, 1))
                
            else:
                # Other profiles rotated
                angle = (idx * 90) % 360  # Rotate by 90 degrees for each profile
                rad = np.radians(angle)
                
                x = distances * np.cos(rad)
                y = distances * np.sin(rad)
                
                # Create surface with rotation
                if angle % 180 == 0:  # Along X
                    Y_mesh = np.linspace(-cross_width/2, cross_width/2, n_cross)
                    X_mesh, Y_mesh = np.meshgrid(x, Y_mesh)
                    Z_mesh = np.tile(elevations, (n_cross, 1))
                else:  # Along Y
                    X_mesh = np.linspace(-cross_width/2, cross_width/2, n_cross)
                    X_mesh, Y_mesh = np.meshgrid(X_mesh, y)
                    Z_mesh = np.tile(elevations, (n_cross, 1)).T
            
            # Plot surface with transparency
            surf = self.ax.plot_surface(X_mesh, Y_mesh, Z_mesh, 
                                       cmap=self.settings.get('colormap', 'terrain'),
                                       alpha=0.6, linewidth=0, antialiased=True)
            
            # Plot main profile line
            self.ax.plot(x, y, elevations, color=color, linewidth=3, 
                        label=f'Profile {idx+1}', zorder=10)
            
            # Add start/end markers
            self.ax.scatter([x[0]], [y[0]], [elevations[0]], 
                          color=color, s=100, marker='o', label=f'Start {idx+1}')
            self.ax.scatter([x[-1]], [y[-1]], [elevations[-1]], 
                          color=color, s=100, marker='s', label=f'End {idx+1}')
        
        # Add intersection point if we have crossing profiles
        if len(self.profile_data_list) >= 2:
            # Simple intersection at origin
            self.ax.scatter([0], [0], [np.mean([p[0][1] for p in self.profile_data_list if p])], 
                          color='yellow', s=200, marker='*', label='Intersection', zorder=20)
        
        # Configure plot
        self.ax.set_xlabel('X (m)', labelpad=10)
        self.ax.set_ylabel('Y (m)', labelpad=10)
        self.ax.set_zlabel('Elevation (m)', labelpad=10)
        self.ax.set_title('Cross-Section 3D Visualization', pad=20)
        
        # Add grid
        if self.settings.get('show_grid', True):
            self.ax.grid(True, alpha=0.3)
        
        # Add legend
        self.ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
        
        # Set initial view
        self.ax.view_init(elev=30, azim=45)
        
        # Adjust layout
        self.figure.tight_layout()
        self.canvas.draw()
        
        QgsMessageLog.logMessage("Cross-section 3D plot created successfully", "DualProfileViewer", Qgis.Info)
        
    def toggle_rotation(self):
        if self.rotate_button.isChecked():
            self.start_rotation()
        else:
            self.stop_rotation()
            
    def start_rotation(self):
        from PyQt5.QtCore import QTimer
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_view)
        self.rotation_timer.start(50)
        
    def stop_rotation(self):
        if self.rotation_timer:
            self.rotation_timer.stop()
            self.rotation_timer = None
            
    def rotate_view(self):
        if hasattr(self, 'ax'):
            current_azim = self.ax.azim
            self.ax.view_init(elev=30, azim=(current_azim + 1) % 360)
            self.canvas.draw()
            
    def reset_view(self):
        if hasattr(self, 'ax'):
            self.ax.view_init(elev=30, azim=45)
            self.canvas.draw()
            
    def closeEvent(self, event):
        self.stop_rotation()
        super().closeEvent(event)