import sys
import os
from typing import Optional, List, Tuple
import numpy as np
from qgis.core import (
    QgsMessageLog, Qgis, QgsPointXY, QgsGeometry, 
    QgsFeature, QgsVectorLayer, QgsWkbTypes
)
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from .simple_3d_viewer import Simple3DViewer

# Try to import plotly viewer
try:
    from .plotly_3d_viewer import Plotly3DViewer, PLOTLY_AVAILABLE
except ImportError:
    PLOTLY_AVAILABLE = False
    
# Import browser-based plotly viewer
try:
    from .plotly_browser_viewer import create_plotly_3d_visualization
    PLOTLY_BROWSER_AVAILABLE = True
except ImportError:
    PLOTLY_BROWSER_AVAILABLE = False

# Module availability flags
STRATIGRAPH_AVAILABLE = False
MAYAVI_AVAILABLE = False

# Try to import stratigraph and related modules
try:
    import stratigraph
    STRATIGRAPH_AVAILABLE = True
    QgsMessageLog.logMessage("Stratigraph module loaded successfully", "DualProfileViewer", Qgis.Info)
except ImportError:
    QgsMessageLog.logMessage("Stratigraph module not available", "DualProfileViewer", Qgis.Warning)

try:
    from mayavi import mlab
    MAYAVI_AVAILABLE = True
    QgsMessageLog.logMessage("Mayavi module loaded successfully", "DualProfileViewer", Qgis.Info)
except ImportError:
    QgsMessageLog.logMessage("Mayavi module not available for 3D visualization", "DualProfileViewer", Qgis.Warning)


class StratigraphIntegration(QObject):
    visualization_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile_data = None
        self.stratigraph_model = None
        
    def is_available(self) -> bool:
        return STRATIGRAPH_AVAILABLE
        
    def is_3d_available(self) -> bool:
        return MAYAVI_AVAILABLE
        
    def load_profile_data(self, profile_points: List[Tuple[float, float, float]]):
        if not STRATIGRAPH_AVAILABLE:
            self.error_occurred.emit("Stratigraph module is not installed")
            return False
            
        try:
            # Convert profile points to numpy array
            self.profile_data = np.array(profile_points)
            QgsMessageLog.logMessage(f"Loaded {len(profile_points)} profile points", "DualProfileViewer", Qgis.Info)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error loading profile data: {str(e)}")
            return False
            
    def create_stratigraphic_model(self, layer_boundaries: Optional[List[float]] = None):
        if not STRATIGRAPH_AVAILABLE or self.profile_data is None:
            self.error_occurred.emit("Cannot create model: stratigraph not available or no data loaded")
            return False
            
        try:
            # Create a basic stratigraphic model from profile data
            # This is a simplified implementation - real usage would depend on data structure
            
            # Extract elevation data
            distances = self.profile_data[:, 0]
            elevations = self.profile_data[:, 1]
            
            # Create synthetic time steps if not provided
            if layer_boundaries is None:
                min_elev = np.min(elevations)
                max_elev = np.max(elevations)
                layer_boundaries = np.linspace(min_elev, max_elev, 10)
            
            # Store model data
            self.stratigraph_model = {
                'distances': distances,
                'elevations': elevations,
                'layer_boundaries': layer_boundaries,
                'profile_data': self.profile_data
            }
            
            QgsMessageLog.logMessage("Stratigraphic model created", "DualProfileViewer", Qgis.Info)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error creating stratigraphic model: {str(e)}")
            return False
            
    def visualize_3d(self, show_layers: bool = True, exploded: bool = False, settings: dict = None, profile_data_list=None):
        # Check if we have profile data
        data_to_use = profile_data_list if profile_data_list else self.profile_data
        
        if data_to_use is None:
            self.error_occurred.emit("No profile data available for visualization")
            return False
            
        if not settings:
            self.error_occurred.emit("No settings provided for visualization")
            return False
            
        try:
            # Try Plotly in browser for advanced features (measurements, export, etc.)
            use_plotly_browser = True  # Set to False to use only matplotlib
            
            if use_plotly_browser and PLOTLY_BROWSER_AVAILABLE:
                try:
                    QgsMessageLog.logMessage("Using browser-based Plotly viewer", "DualProfileViewer", Qgis.Info)
                    success, message = create_plotly_3d_visualization(data_to_use, settings)
                    if success:
                        QMessageBox.information(None, "3D Visualization", message)
                        return True
                    else:
                        QgsMessageLog.logMessage(f"Browser viewer failed: {message}", "DualProfileViewer", Qgis.Warning)
                except Exception as e:
                    QgsMessageLog.logMessage(f"Browser viewer error: {str(e)}", "DualProfileViewer", Qgis.Warning)
            
            # Final fallback to matplotlib
            QgsMessageLog.logMessage("Using matplotlib 3D viewer", "DualProfileViewer", Qgis.Info)
            
            # First test if matplotlib works at all
            test_matplotlib = False  # Set to True to show test
            if test_matplotlib:
                try:
                    from .basic_3d_test import show_basic_3d_test
                    QgsMessageLog.logMessage("Showing basic 3D test first", "DualProfileViewer", Qgis.Info)
                    show_basic_3d_test()
                    return True
                except Exception as e:
                    QgsMessageLog.logMessage(f"Basic test failed: {str(e)}", "DualProfileViewer", Qgis.Warning)
            
            # Check if we have valid data
            if not data_to_use or (isinstance(data_to_use, list) and len(data_to_use) == 0):
                QgsMessageLog.logMessage("No data available, showing test visualization", "DualProfileViewer", Qgis.Warning)
                try:
                    from .simple_test_3d import show_test_3d_viewer
                    show_test_3d_viewer()
                    QMessageBox.information(None, "Test Data", 
                                          "Showing test visualization. Create profiles first to see your actual data.")
                except Exception as e:
                    QgsMessageLog.logMessage(f"Test viewer failed: {str(e)}", "DualProfileViewer", Qgis.Critical)
                return True
                
            # Try the actual viewer
            try:
                # Check if we have multiple profiles for cross-sections
                if isinstance(data_to_use, list) and len(data_to_use) > 1:
                    QgsMessageLog.logMessage("Creating CrossSection3DViewer for multiple profiles", "DualProfileViewer", Qgis.Info)
                    from .cross_section_3d_viewer import CrossSection3DViewer
                    viewer = CrossSection3DViewer(data_to_use, settings)
                else:
                    QgsMessageLog.logMessage("Creating Simple3DViewer for single profile", "DualProfileViewer", Qgis.Info)
                    viewer = Simple3DViewer(data_to_use, settings)
                    
                QgsMessageLog.logMessage("Showing 3D viewer", "DualProfileViewer", Qgis.Info)
                viewer.exec_()
                return True
            except Exception as e:
                QgsMessageLog.logMessage(f"Simple3DViewer failed: {str(e)}", "DualProfileViewer", Qgis.Critical)
                import traceback
                QgsMessageLog.logMessage(traceback.format_exc(), "DualProfileViewer", Qgis.Critical)
                
                # Last resort - show error dialog
                QMessageBox.critical(None, "3D Visualization Error", 
                                   f"Failed to create 3D visualization:\n{str(e)}\n\n"
                                   "Please check the log messages for details.")
                return False
            
        except Exception as e:
            self.error_occurred.emit(f"Error creating 3D visualization: {str(e)}")
            QgsMessageLog.logMessage(f"Visualization error: {str(e)}", "DualProfileViewer", Qgis.Critical)
            import traceback
            QgsMessageLog.logMessage(traceback.format_exc(), "DualProfileViewer", Qgis.Critical)
            return False
            
    def create_wheeler_diagram(self):
        if not STRATIGRAPH_AVAILABLE or self.stratigraph_model is None:
            self.error_occurred.emit("Cannot create Wheeler diagram: requirements not met")
            return None
            
        try:
            # Create a Wheeler (chronostratigraphic) diagram
            # This is a placeholder - actual implementation would use stratigraph functions
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            distances = self.stratigraph_model['distances']
            elevations = self.stratigraph_model['elevations']
            
            # Simple time-space diagram
            ax.plot(distances, elevations, 'k-', linewidth=2)
            ax.fill_between(distances, elevations, alpha=0.3)
            
            ax.set_xlabel('Distance (m)')
            ax.set_ylabel('Time/Elevation')
            ax.set_title('Wheeler Diagram (Chronostratigraphic View)')
            ax.grid(True, alpha=0.3)
            
            return fig
            
        except Exception as e:
            self.error_occurred.emit(f"Error creating Wheeler diagram: {str(e)}")
            return None
            
    def export_to_stratigraph_format(self, output_path: str):
        if self.stratigraph_model is None:
            self.error_occurred.emit("No model to export")
            return False
            
        try:
            # Export data in a format compatible with stratigraph
            data = {
                'type': 'profile_section',
                'distances': self.stratigraph_model['distances'].tolist(),
                'elevations': self.stratigraph_model['elevations'].tolist(),
                'layer_boundaries': self.stratigraph_model['layer_boundaries'].tolist() 
                    if 'layer_boundaries' in self.stratigraph_model else []
            }
            
            import json
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            QgsMessageLog.logMessage(f"Exported to {output_path}", "DualProfileViewer", Qgis.Info)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error exporting data: {str(e)}")
            return False