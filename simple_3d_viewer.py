"""
Simple 3D viewer using matplotlib for stratigraphic visualization
This doesn't require mayavi or stratigraph, only matplotlib
"""

import numpy as np
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from mpl_toolkits.mplot3d import Axes3D
except ImportError as e:
    raise ImportError(f"Matplotlib is required for 3D visualization: {e}")
    
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt


class Simple3DViewer(QDialog):
    def __init__(self, profile_data, settings, parent=None):
        super().__init__(parent)
        
        from qgis.core import QgsMessageLog, Qgis
        QgsMessageLog.logMessage("Simple3DViewer initializing", "DualProfileViewer", Qgis.Info)
        
        self.profile_data = profile_data
        self.settings = settings
        self.setWindowTitle("3D Profile Visualization")
        self.setMinimumSize(800, 600)
        
        try:
            self.init_ui()
            QgsMessageLog.logMessage("UI initialized", "DualProfileViewer", Qgis.Info)
            self.create_3d_plot()
            QgsMessageLog.logMessage("3D plot created", "DualProfileViewer", Qgis.Info)
        except Exception as e:
            QgsMessageLog.logMessage(f"Error in Simple3DViewer: {str(e)}", "DualProfileViewer", Qgis.Critical)
            import traceback
            QgsMessageLog.logMessage(traceback.format_exc(), "DualProfileViewer", Qgis.Critical)
        
    def init_ui(self):
        layout = QVBoxLayout()
        
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
        
        # Create 3D subplot
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        if not self.profile_data:
            self.ax.text(0.5, 0.5, 0.5, 'No profile data available', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        from qgis.core import QgsMessageLog, Qgis
        QgsMessageLog.logMessage(f"Profile data type: {type(self.profile_data)}", "DualProfileViewer", Qgis.Info)
        QgsMessageLog.logMessage(f"Profile data length: {len(self.profile_data) if hasattr(self.profile_data, '__len__') else 'N/A'}", "DualProfileViewer", Qgis.Info)
            
        # Extract profile data
        try:
            # Handle different data formats
            if isinstance(self.profile_data, list) and len(self.profile_data) > 0:
                # Check if it's a list of profiles
                if isinstance(self.profile_data[0], list) or (isinstance(self.profile_data[0], np.ndarray) and len(self.profile_data[0].shape) > 1):
                    QgsMessageLog.logMessage("Detected multiple profiles, using first one", "DualProfileViewer", Qgis.Info)
                    profile_array = np.array(self.profile_data[0])
                else:
                    profile_array = np.array(self.profile_data)
            else:
                profile_array = np.array(self.profile_data)
                
            QgsMessageLog.logMessage(f"Profile array shape: {profile_array.shape}", "DualProfileViewer", Qgis.Info)
            
            # Ensure we have a 2D array
            if len(profile_array.shape) == 3 and profile_array.shape[0] > 1:
                # Multiple profiles, use first
                profile_array = profile_array[0]
                QgsMessageLog.logMessage(f"Using first profile, new shape: {profile_array.shape}", "DualProfileViewer", Qgis.Info)
            
            if len(profile_array.shape) < 2 or profile_array.shape[1] < 2:
                QgsMessageLog.logMessage("Invalid profile data shape", "DualProfileViewer", Qgis.Warning)
                self.ax.text(0.5, 0.5, 0.5, 'Invalid profile data format', 
                            ha='center', va='center', transform=self.ax.transAxes)
                self.canvas.draw()
                return
                
            distances = profile_array[:, 0]
            elevations = profile_array[:, 1]
            
            QgsMessageLog.logMessage(f"Distances range: {np.min(distances):.2f} to {np.max(distances):.2f}", "DualProfileViewer", Qgis.Info)
            QgsMessageLog.logMessage(f"Elevations range: {np.min(elevations):.2f} to {np.max(elevations):.2f}", "DualProfileViewer", Qgis.Info)
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error extracting profile data: {str(e)}", "DualProfileViewer", Qgis.Critical)
            self.ax.text(0.5, 0.5, 0.5, f'Error: {str(e)}', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Create cross-section width
        cross_width = self.settings.get('cross_width', 100)
        n_cross = 10  # Number of cross-section lines
        
        # Create mesh grid
        y_positions = np.linspace(-cross_width/2, cross_width/2, n_cross)
        X, Y = np.meshgrid(distances, y_positions)
        
        # Replicate elevations for each cross-section line
        Z = np.tile(elevations, (n_cross, 1))
        
        # Add some variation if requested
        if self.settings.get('show_layers', True):
            # Add synthetic layering effect
            layer_count = self.settings.get('layer_count', 10)
            layer_thickness = (np.max(elevations) - np.min(elevations)) / layer_count
            
            for i in range(layer_count):
                layer_elevation = np.min(elevations) + i * layer_thickness
                # Add slight undulation to layers
                layer_variation = np.sin(distances / np.max(distances) * 2 * np.pi) * 0.5
                # Ensure layer_variation has the right shape
                layer_var_2d = np.tile(layer_variation, (n_cross, 1))
                # Apply variation only where Z is above the layer elevation
                mask = Z > layer_elevation
                Z = np.where(mask, Z + layer_var_2d * 0.1, Z)
        
        # Plot the surface
        colormap = self.settings.get('colormap', 'terrain')
        surf = self.ax.plot_surface(X, Y, Z, cmap=colormap, 
                                   alpha=0.8, linewidth=0, 
                                   antialiased=True, shade=True)
        
        # Add layer boundaries if requested
        if self.settings.get('show_layers', True):
            layer_count = self.settings.get('layer_count', 10)
            elevations_range = np.linspace(np.min(Z), np.max(Z), layer_count)
            
            for elev in elevations_range[1:-1]:
                # Create contour at this elevation
                self.ax.contour(X, Y, Z, levels=[elev], 
                              colors='black', alpha=0.3, linewidths=0.5)
        
        # Add grid if requested
        if self.settings.get('show_grid', True):
            self.ax.grid(True, alpha=0.3)
            
        # Set labels and title
        self.ax.set_xlabel('Distance (m)', labelpad=10)
        self.ax.set_ylabel('Cross-section (m)', labelpad=10)
        self.ax.set_zlabel('Elevation (m)', labelpad=10)
        self.ax.set_title('3D Stratigraphic Profile Visualization', pad=20)
        
        # Add colorbar
        self.figure.colorbar(surf, ax=self.ax, shrink=0.5, aspect=5)
        
        # Set initial view angle
        self.ax.view_init(elev=30, azim=45)
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Force canvas update
        self.canvas.draw()
        self.canvas.flush_events()
        
        # Log success
        QgsMessageLog.logMessage("3D plot created successfully", "DualProfileViewer", Qgis.Info)
        
    def toggle_rotation(self):
        if self.rotate_button.isChecked():
            self.start_rotation()
        else:
            self.stop_rotation()
            
    def start_rotation(self):
        from PyQt5.QtCore import QTimer
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_view)
        self.rotation_timer.start(50)  # Update every 50ms
        
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