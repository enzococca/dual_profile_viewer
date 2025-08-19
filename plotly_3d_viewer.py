"""
Advanced 3D viewer using Plotly for interactive stratigraphic visualization
Supports cross-sections, measurements, and textures
"""

import numpy as np
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QCheckBox, QLabel, QSpinBox, QGroupBox, QComboBox,
    QMessageBox, QToolBar, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl

# Try to import QWebEngineView
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    try:
        from PyQt5.QtWebKitWidgets import QWebView as QWebEngineView
        WEBENGINE_AVAILABLE = True
    except ImportError:
        WEBENGINE_AVAILABLE = False
import json
import tempfile
import os

# Check if plotly is available
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class Plotly3DViewer(QDialog):
    measurement_requested = pyqtSignal(dict)
    
    def __init__(self, profile_data_list, settings, parent=None):
        super().__init__(parent)
        # Handle both single profile and list of profiles
        if isinstance(profile_data_list, list):
            # Check if it's a list of profiles or a single profile as list of points
            if profile_data_list and isinstance(profile_data_list[0], list):
                self.profile_data_list = profile_data_list
            else:
                self.profile_data_list = [profile_data_list]
        else:
            self.profile_data_list = [profile_data_list]
        self.settings = settings
        self.setWindowTitle("Interactive 3D Profile Visualization")
        self.setMinimumSize(1000, 700)
        self.measurement_mode = False
        self.init_ui()
        self.create_3d_plot()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar for controls
        toolbar = QToolBar()
        
        # Measurement tool
        self.measure_action = QAction("📏 Measure", self)
        self.measure_action.setCheckable(True)
        self.measure_action.triggered.connect(self.toggle_measurement)
        toolbar.addAction(self.measure_action)
        
        toolbar.addSeparator()
        
        # Cross-section controls
        self.show_intersection = QCheckBox("Show Intersection")
        self.show_intersection.setChecked(True)
        self.show_intersection.stateChanged.connect(self.update_plot)
        toolbar.addWidget(self.show_intersection)
        
        # Texture options
        toolbar.addWidget(QLabel("Texture:"))
        self.texture_combo = QComboBox()
        self.texture_combo.addItems(['None', 'Geological', 'Elevation', 'Gradient', 'Custom'])
        self.texture_combo.currentTextChanged.connect(self.update_plot)
        toolbar.addWidget(self.texture_combo)
        
        layout.addWidget(toolbar)
        
        # Web view for Plotly
        if WEBENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            layout.addWidget(self.web_view)
        else:
            # Fallback to simple message
            from PyQt5.QtWidgets import QTextEdit
            self.web_view = QTextEdit()
            self.web_view.setReadOnly(True)
            layout.addWidget(self.web_view)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export 3D Model")
        self.export_button.clicked.connect(self.export_model)
        button_layout.addWidget(self.export_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def create_3d_plot(self):
        if not PLOTLY_AVAILABLE:
            # Fallback message
            html = """
            <html><body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Plotly not available</h2>
            <p>Install plotly for interactive 3D visualization:</p>
            <code>pip install plotly</code>
            </body></html>
            """
            self.web_view.setHtml(html)
            return
            
        fig = go.Figure()
        
        # Process each profile (for cross-sections)
        for i, profile_data in enumerate(self.profile_data_list):
            if not profile_data:
                continue
                
            # Extract profile data
            profile_array = np.array(profile_data)
            distances = profile_array[:, 0]
            elevations = profile_array[:, 1]
            
            # Create cross-section mesh
            cross_width = self.settings.get('cross_width', 100)
            n_cross = 20  # More points for smoother surface
            
            # For cross-sections, rotate profiles
            if i == 0:
                # First profile along X axis
                x = distances
                y = np.zeros_like(distances)
                z = elevations
            else:
                # Second profile along Y axis (creating intersection)
                x = np.zeros_like(distances)
                y = distances
                z = elevations
                
            # Create surface mesh for each profile
            if i == 0:
                Y_mesh = np.linspace(-cross_width/2, cross_width/2, n_cross)
                X_mesh, Y_mesh = np.meshgrid(x, Y_mesh)
                Z_mesh = np.tile(z, (n_cross, 1))
            else:
                X_mesh = np.linspace(-cross_width/2, cross_width/2, n_cross)
                X_mesh, Y_mesh = np.meshgrid(X_mesh, y)
                Z_mesh = np.tile(z, (n_cross, 1)).T
                
            # Apply texture based on selection
            texture = self.create_texture(Z_mesh, self.texture_combo.currentText())
            
            # Add surface
            surface = go.Surface(
                x=X_mesh,
                y=Y_mesh,
                z=Z_mesh,
                colorscale=self.get_valid_colorscale(self.settings.get('colormap', 'earth')),
                name=f'Profile {i+1}',
                showscale=i == 0,  # Only show colorbar for first profile
                opacity=0.9,
                surfacecolor=texture if texture is not None else Z_mesh,
                text=self.create_hover_text(X_mesh, Y_mesh, Z_mesh),
                hovertemplate='X: %{x:.1f}m<br>Y: %{y:.1f}m<br>Z: %{z:.1f}m<br>%{text}<extra></extra>'
            )
            fig.add_trace(surface)
            
            # Add profile lines for clarity
            fig.add_trace(go.Scatter3d(
                x=x,
                y=y,
                z=z,
                mode='lines',
                line=dict(color='red' if i == 0 else 'blue', width=4),
                name=f'Profile Line {i+1}'
            ))
            
            # Add layers if requested
            if self.settings.get('show_layers', True):
                self.add_layers(fig, X_mesh, Y_mesh, Z_mesh, i)
                
        # Add intersection highlight if multiple profiles
        if len(self.profile_data_list) > 1 and self.show_intersection.isChecked():
            self.add_intersection_markers(fig)
            
        # Configure layout
        fig.update_layout(
            title='3D Cross-Section Visualization',
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Elevation (m)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=0.5)
            ),
            showlegend=True,
            hovermode='closest'
        )
        
        # Add measurement capability
        if self.measurement_mode:
            fig.update_layout(dragmode='select')
            
        # Convert to HTML
        html = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')
        
        # Add custom JavaScript for measurements
        if self.measurement_mode:
            html = self.add_measurement_js(html)
            
        # Display in web view
        full_html = f"""
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; }}
                #myDiv {{ width: 100%; height: 100%; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Save to temp file and load
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(full_html)
            temp_path = f.name
            
        if WEBENGINE_AVAILABLE:
            self.web_view.load(QUrl.fromLocalFile(temp_path))
        else:
            # For QTextEdit fallback, just set the HTML
            self.web_view.setHtml(full_html)
        
    def get_valid_colorscale(self, colormap):
        """Convert matplotlib colormap names to valid Plotly colorscales"""
        colormap_mapping = {
            'terrain': 'earth',
            'viridis': 'viridis',
            'plasma': 'plasma',
            'coolwarm': 'bluered',
            'seismic': 'rdbu'
        }
        return colormap_mapping.get(colormap, 'earth')
        
    def create_texture(self, Z_mesh, texture_type):
        """Create texture for the surface based on type"""
        if texture_type == 'None':
            return None
        elif texture_type == 'Gradient':
            # Calculate gradient magnitude
            gy, gx = np.gradient(Z_mesh)
            gradient_magnitude = np.sqrt(gx**2 + gy**2)
            return gradient_magnitude
        elif texture_type == 'Geological':
            # Simple geological layers based on elevation
            layers = np.digitize(Z_mesh, np.percentile(Z_mesh, [20, 40, 60, 80]))
            return layers
        elif texture_type == 'Elevation':
            return Z_mesh
        else:
            return None
            
    def create_hover_text(self, X, Y, Z):
        """Create informative hover text"""
        gradient_y, gradient_x = np.gradient(Z)
        slope = np.degrees(np.arctan(np.sqrt(gradient_x**2 + gradient_y**2)))
        
        text = []
        for i in range(X.shape[0]):
            row_text = []
            for j in range(X.shape[1]):
                row_text.append(f"Slope: {slope[i,j]:.1f}°")
            text.append(row_text)
        return text
        
    def add_layers(self, fig, X, Y, Z, profile_idx):
        """Add stratigraphic layers to the visualization"""
        layer_count = self.settings.get('layer_count', 10)
        z_min, z_max = np.min(Z), np.max(Z)
        layer_elevations = np.linspace(z_min, z_max, layer_count)
        
        for elev in layer_elevations[1:-1]:
            # Create contour at elevation
            contour = go.Scatter3d(
                x=X.flatten(),
                y=Y.flatten(),
                z=np.full(X.size, elev),
                mode='markers',
                marker=dict(size=1, color='gray', opacity=0.3),
                name=f'Layer at {elev:.1f}m',
                showlegend=False
            )
            fig.add_trace(contour)
            
    def add_intersection_markers(self, fig):
        """Add markers where profiles intersect"""
        # This is simplified - in reality you'd calculate actual intersection
        fig.add_trace(go.Scatter3d(
            x=[0],
            y=[0],
            z=[np.mean([p[0][1] for p in self.profile_data_list])],
            mode='markers+text',
            marker=dict(size=10, color='yellow', symbol='diamond'),
            text=['Intersection'],
            textposition='top center',
            name='Intersection Point'
        ))
        
    def add_measurement_js(self, html):
        """Add JavaScript for distance measurement"""
        js_code = """
        <script>
        var measurePoints = [];
        document.getElementById('myDiv').on('plotly_click', function(data){
            if(measurePoints.length < 2) {
                var pt = data.points[0];
                measurePoints.push({x: pt.x, y: pt.y, z: pt.z});
                
                if(measurePoints.length == 2) {
                    var dist = Math.sqrt(
                        Math.pow(measurePoints[1].x - measurePoints[0].x, 2) +
                        Math.pow(measurePoints[1].y - measurePoints[0].y, 2) +
                        Math.pow(measurePoints[1].z - measurePoints[0].z, 2)
                    );
                    alert('Distance: ' + dist.toFixed(2) + ' m');
                    measurePoints = [];
                }
            }
        });
        </script>
        """
        return html + js_code
        
    def toggle_measurement(self):
        """Toggle measurement mode"""
        self.measurement_mode = self.measure_action.isChecked()
        if self.measurement_mode:
            QMessageBox.information(self, "Measurement Mode", 
                                  "Click two points to measure distance")
        self.update_plot()
        
    def update_plot(self):
        """Update the plot with new settings"""
        self.create_3d_plot()
        
    def export_model(self):
        """Export 3D model in various formats"""
        # This would export to formats like OBJ, STL, etc.
        QMessageBox.information(self, "Export", 
                              "3D model export functionality would be implemented here")