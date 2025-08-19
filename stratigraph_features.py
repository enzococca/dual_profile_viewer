import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from qgis.core import QgsMessageLog, Qgis
from PyQt5.QtCore import QObject, pyqtSignal

# Check if stratigraph specific functions are available
STRATIGRAPH_ADVANCED = False
try:
    import stratigraph
    # Check for advanced features
    if hasattr(stratigraph, 'create_wheeler_diagram'):
        STRATIGRAPH_ADVANCED = True
except ImportError:
    pass


class StratigraphFeatures(QObject):
    analysis_complete = pyqtSignal(dict)
    progress_update = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile_data = None
        self.stratigraphic_layers = []
        
    def analyze_stratigraphy(self, profile_data: np.ndarray, 
                           layer_detection_threshold: float = 0.5) -> Dict:
        """Analyze profile data to detect stratigraphic layers"""
        self.progress_update.emit("Analyzing stratigraphic layers...")
        
        distances = profile_data[:, 0]
        elevations = profile_data[:, 1]
        
        # Simple layer detection based on elevation changes
        # This is a simplified algorithm - real implementation would be more sophisticated
        
        # Calculate gradient
        gradient = np.gradient(elevations)
        
        # Find significant changes in gradient (potential layer boundaries)
        layer_indices = []
        for i in range(1, len(gradient) - 1):
            if abs(gradient[i] - gradient[i-1]) > layer_detection_threshold:
                layer_indices.append(i)
                
        # Create layer information
        layers = []
        prev_idx = 0
        
        for idx in layer_indices:
            layer = {
                'start_distance': distances[prev_idx],
                'end_distance': distances[idx],
                'start_elevation': elevations[prev_idx],
                'end_elevation': elevations[idx],
                'thickness': abs(elevations[idx] - elevations[prev_idx]),
                'slope': (elevations[idx] - elevations[prev_idx]) / (distances[idx] - distances[prev_idx])
            }
            layers.append(layer)
            prev_idx = idx
            
        # Add final layer
        if prev_idx < len(distances) - 1:
            layer = {
                'start_distance': distances[prev_idx],
                'end_distance': distances[-1],
                'start_elevation': elevations[prev_idx],
                'end_elevation': elevations[-1],
                'thickness': abs(elevations[-1] - elevations[prev_idx]),
                'slope': (elevations[-1] - elevations[prev_idx]) / (distances[-1] - distances[prev_idx])
            }
            layers.append(layer)
            
        self.stratigraphic_layers = layers
        
        # Calculate statistics
        analysis_results = {
            'num_layers': len(layers),
            'total_thickness': max(elevations) - min(elevations),
            'average_layer_thickness': np.mean([l['thickness'] for l in layers]) if layers else 0,
            'layers': layers,
            'profile_length': distances[-1] - distances[0],
            'elevation_range': (min(elevations), max(elevations))
        }
        
        self.progress_update.emit(f"Detected {len(layers)} stratigraphic layers")
        self.analysis_complete.emit(analysis_results)
        
        return analysis_results
        
    def calculate_deposition_rates(self, time_intervals: Optional[List[float]] = None) -> List[Dict]:
        """Calculate theoretical deposition rates for layers"""
        if not self.stratigraphic_layers:
            return []
            
        if time_intervals is None:
            # Assume uniform time intervals
            time_intervals = list(range(len(self.stratigraphic_layers) + 1))
            
        deposition_rates = []
        
        for i, layer in enumerate(self.stratigraphic_layers):
            if i < len(time_intervals) - 1:
                time_span = time_intervals[i+1] - time_intervals[i]
                rate = layer['thickness'] / time_span if time_span > 0 else 0
                
                deposition_rates.append({
                    'layer_index': i,
                    'thickness': layer['thickness'],
                    'time_span': time_span,
                    'deposition_rate': rate,
                    'rate_units': 'm/time_unit'
                })
                
        return deposition_rates
        
    def generate_synthetic_boreholes(self, num_boreholes: int = 5, 
                                   lateral_offset: float = 10.0) -> List[Dict]:
        """Generate synthetic borehole data from the profile"""
        if not self.profile_data:
            return []
            
        boreholes = []
        distances = self.profile_data[:, 0]
        
        # Generate boreholes at regular intervals
        borehole_distances = np.linspace(distances[0], distances[-1], num_boreholes)
        
        for i, dist in enumerate(borehole_distances):
            # Find closest profile point
            idx = np.argmin(np.abs(distances - dist))
            
            # Create borehole data
            borehole = {
                'id': f'BH-{i+1}',
                'distance': dist,
                'surface_elevation': self.profile_data[idx, 1],
                'x': self.profile_data[idx, 0],  # Assuming x coordinate is stored
                'y': lateral_offset * (i - num_boreholes/2),  # Spread boreholes laterally
                'layers': []
            }
            
            # Add layer information
            current_elevation = borehole['surface_elevation']
            for layer in self.stratigraphic_layers:
                if layer['start_distance'] <= dist <= layer['end_distance']:
                    # Interpolate layer boundaries at this distance
                    layer_info = {
                        'top': current_elevation,
                        'bottom': current_elevation - layer['thickness'],
                        'thickness': layer['thickness'],
                        'lithology': f'Layer {len(borehole["layers"]) + 1}'
                    }
                    borehole['layers'].append(layer_info)
                    current_elevation = layer_info['bottom']
                    
            boreholes.append(borehole)
            
        return boreholes
        
    def export_for_3d_modeling(self, output_format: str = 'json') -> Dict:
        """Export data formatted for 3D stratigraphic modeling"""
        export_data = {
            'type': 'stratigraphic_profile',
            'metadata': {
                'num_points': len(self.profile_data) if self.profile_data is not None else 0,
                'num_layers': len(self.stratigraphic_layers),
                'units': 'meters'
            },
            'profile': {
                'points': self.profile_data.tolist() if self.profile_data is not None else [],
                'layers': self.stratigraphic_layers
            },
            'analysis': {
                'deposition_rates': self.calculate_deposition_rates(),
                'synthetic_boreholes': self.generate_synthetic_boreholes()
            }
        }
        
        return export_data
        
    def create_fence_diagram_data(self, parallel_profiles: List[np.ndarray]) -> Dict:
        """Create data for fence diagram visualization"""
        fence_data = {
            'profiles': [],
            'connections': []
        }
        
        for i, profile in enumerate(parallel_profiles):
            profile_data = {
                'id': f'Profile_{i}',
                'points': profile.tolist(),
                'layers': self.analyze_stratigraphy(profile)['layers']
            }
            fence_data['profiles'].append(profile_data)
            
            # Create connections between adjacent profiles
            if i > 0:
                fence_data['connections'].append({
                    'from': f'Profile_{i-1}',
                    'to': f'Profile_{i}'
                })
                
        return fence_data