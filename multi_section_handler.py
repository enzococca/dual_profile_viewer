# -*- coding: utf-8 -*-
"""
Multi-Section Handler for Polygon Profiles
Handles creation and visualization of multiple sections from polygon drawing
"""

import numpy as np
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsGeometry, QgsPointXY, QgsMessageLog, Qgis

class MultiSectionHandler:
    """Handles multiple sections from polygon drawing"""
    
    @staticmethod
    def process_polygon_sections(polygon_data, dem_layer, multi_dem_widget, num_samples=200):
        """Process all sections from a polygon"""
        sections = polygon_data.get('sections', [])
        all_section_data = []
        
        for idx, section in enumerate(sections):
            # Extract profile for this section
            line = section['line']
            points = line.asPolyline() if not line.isMultipart() else line.asMultiPolyline()[0]
            
            if len(points) >= 2:
                # Sample elevation along this section
                profile_data = MultiSectionHandler.sample_section(
                    dem_layer, points[0], points[1], num_samples
                )
                
                # Add section metadata
                profile_data['section_index'] = idx
                profile_data['section_name'] = f"Side {idx + 1}"
                profile_data['start_point'] = section['start']
                profile_data['end_point'] = section['end']
                profile_data['line_geometry'] = line
                profile_data['polygon_geometry'] = section['polygon']
                profile_data['width'] = section['width']
                
                all_section_data.append(profile_data)
        
        return all_section_data
    
    @staticmethod
    def sample_section(raster_layer, start_point, end_point, num_samples):
        """Sample elevation along a section line"""
        # Calculate distance
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        total_distance = np.sqrt(dx**2 + dy**2)
        
        # Create sample points
        distances = np.linspace(0, total_distance, num_samples)
        elevations = []
        
        # Sample elevation at each point
        for i, dist in enumerate(distances):
            # Calculate position
            ratio = dist / total_distance if total_distance > 0 else 0
            x = start_point.x() + ratio * dx
            y = start_point.y() + ratio * dy
            
            # Sample raster
            value, ok = raster_layer.dataProvider().sample(QgsPointXY(x, y), 1)
            
            if ok and value is not None:
                elevations.append(float(value))
            else:
                elevations.append(np.nan)
        
        return {
            'distances': distances,
            'elevations': np.array(elevations, dtype=np.float64),
            'total_distance': total_distance,
            'start': start_point,
            'end': end_point
        }
    
    @staticmethod
    def create_multi_section_plots(sections_data, use_plotly=True):
        """Create plots for multiple sections"""
        if use_plotly:
            return MultiSectionHandler.create_plotly_multi_section(sections_data)
        else:
            return MultiSectionHandler.create_matplotlib_multi_section(sections_data)
    
    @staticmethod
    def create_plotly_multi_section(sections_data):
        """Create Plotly figure with multiple sections"""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            n_sections = len(sections_data)
            
            # Create subplot layout
            if n_sections <= 2:
                rows, cols = 1, n_sections
            elif n_sections <= 4:
                rows, cols = 2, 2
            elif n_sections <= 6:
                rows, cols = 2, 3
            else:
                rows = int(np.ceil(n_sections / 3))
                cols = 3
            
            # Create subplot titles
            subplot_titles = [f"Section {i+1}: Side {i+1}" for i in range(n_sections)]
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=subplot_titles,
                shared_yaxes=True,
                vertical_spacing=0.1,
                horizontal_spacing=0.05
            )
            
            # Add each section
            for idx, section_data in enumerate(sections_data):
                row = idx // cols + 1
                col = idx % cols + 1
                
                fig.add_trace(
                    go.Scatter(
                        x=section_data['distances'],
                        y=section_data['elevations'],
                        mode='lines',
                        name=section_data['section_name'],
                        line=dict(width=2),
                        showlegend=True
                    ),
                    row=row, col=col
                )
                
                # Update axes
                fig.update_xaxes(title_text="Distance (m)", row=row, col=col)
                if col == 1:
                    fig.update_yaxes(title_text="Elevation (m)", row=row, col=col)
            
            # Update layout
            fig.update_layout(
                title="Polygon Section Profiles",
                height=300 * rows,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error creating plotly figure: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
            return None
    
    @staticmethod
    def create_matplotlib_multi_section(sections_data):
        """Create matplotlib figure with multiple sections"""
        try:
            import matplotlib.pyplot as plt
            
            n_sections = len(sections_data)
            
            # Determine subplot layout
            if n_sections <= 2:
                rows, cols = 1, n_sections
            elif n_sections <= 4:
                rows, cols = 2, 2
            elif n_sections <= 6:
                rows, cols = 2, 3
            else:
                rows = int(np.ceil(n_sections / 3))
                cols = 3
            
            # Create figure
            fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows), 
                                   sharey=True, squeeze=False)
            
            # Flatten axes array for easier iteration
            axes_flat = axes.flatten()
            
            # Plot each section
            for idx, section_data in enumerate(sections_data):
                if idx < len(axes_flat):
                    ax = axes_flat[idx]
                    ax.plot(section_data['distances'], section_data['elevations'], 
                           'b-', linewidth=2)
                    ax.set_title(f"Section {idx+1}: {section_data['section_name']}")
                    ax.set_xlabel('Distance (m)')
                    if idx % cols == 0:
                        ax.set_ylabel('Elevation (m)')
                    ax.grid(True, alpha=0.3)
            
            # Hide unused subplots
            for idx in range(n_sections, len(axes_flat)):
                axes_flat[idx].set_visible(False)
            
            plt.suptitle('Polygon Section Profiles', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error creating matplotlib figure: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
            return None
    
    @staticmethod
    def calculate_multi_section_statistics(sections_data):
        """Calculate statistics for all sections"""
        stats = {}
        
        for idx, section_data in enumerate(sections_data):
            elevations = np.asarray(section_data['elevations'], dtype=np.float64)
            valid_elevations = elevations[~np.isnan(elevations)]
            
            section_stats = {
                'name': section_data['section_name'],
                'length': section_data['total_distance'],
                'min_elevation': np.min(valid_elevations) if len(valid_elevations) > 0 else np.nan,
                'max_elevation': np.max(valid_elevations) if len(valid_elevations) > 0 else np.nan,
                'mean_elevation': np.mean(valid_elevations) if len(valid_elevations) > 0 else np.nan,
                'std_elevation': np.std(valid_elevations) if len(valid_elevations) > 0 else np.nan,
                'elevation_range': (np.max(valid_elevations) - np.min(valid_elevations)) 
                                 if len(valid_elevations) > 0 else np.nan
            }
            
            stats[f'section_{idx}'] = section_stats
        
        # Overall statistics
        all_elevations = []
        total_length = 0
        for section_data in sections_data:
            elevs = np.asarray(section_data['elevations'], dtype=np.float64)
            valid_mask = ~np.isnan(elevs)
            all_elevations.extend(elevs[valid_mask].tolist())
            total_length += section_data['total_distance']
        
        if all_elevations:
            stats['overall'] = {
                'total_length': total_length,
                'min_elevation': np.min(all_elevations),
                'max_elevation': np.max(all_elevations),
                'mean_elevation': np.mean(all_elevations),
                'elevation_range': np.max(all_elevations) - np.min(all_elevations)
            }
        
        return stats
    
    @staticmethod
    def format_statistics_text(stats):
        """Format statistics as text"""
        text = "📊 POLYGON SECTION STATISTICS\n"
        text += "━" * 40 + "\n\n"
        
        # Overall stats
        if 'overall' in stats:
            overall = stats['overall']
            text += "OVERALL:\n"
            text += f"  Total Length: {overall['total_length']:.2f} m\n"
            text += f"  Min Elevation: {overall['min_elevation']:.3f} m\n"
            text += f"  Max Elevation: {overall['max_elevation']:.3f} m\n"
            text += f"  Mean Elevation: {overall['mean_elevation']:.3f} m\n"
            text += f"  Elevation Range: {overall['elevation_range']:.3f} m\n\n"
        
        # Individual section stats
        text += "INDIVIDUAL SECTIONS:\n"
        for key in sorted(stats.keys()):
            if key.startswith('section_'):
                section = stats[key]
                text += f"\n{section['name']}:\n"
                text += f"  Length: {section['length']:.2f} m\n"
                text += f"  Min: {section['min_elevation']:.3f} m\n"
                text += f"  Max: {section['max_elevation']:.3f} m\n"
                text += f"  Mean: {section['mean_elevation']:.3f} m\n"
                text += f"  Range: {section['elevation_range']:.3f} m\n"
        
        return text