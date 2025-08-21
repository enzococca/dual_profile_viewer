# -*- coding: utf-8 -*-
"""
Multi-Section 3D Viewer Extension
Handles 3D visualization of multiple polygon sections
"""

import numpy as np
from qgis.core import QgsMessageLog, Qgis, QgsPointXY

class MultiSection3DViewer:
    """Extension for 3D visualization of multiple sections"""
    
    @staticmethod
    def add_polygon_sections_to_viewer(viewer, sections_data, show_intersections=True):
        """Add multiple polygon sections to 3D viewer"""
        try:
            import pyvista as pv
            
            # Clear existing data
            viewer.plotter.clear()
            viewer.walls = []
            viewer.wall_actors = []
            
            # Color palette for sections
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'cyan']
            
            # Add each section as a wall
            for idx, section_data in enumerate(sections_data):
                color = colors[idx % len(colors)]
                
                # Create wall from section
                wall_mesh = MultiSection3DViewer.create_section_wall(
                    section_data, 
                    viewer.thickness_slider.value(),
                    viewer.exag_slider.value() / 10.0
                )
                
                if wall_mesh:
                    # Add to viewer
                    actor = viewer.plotter.add_mesh(
                        wall_mesh,
                        color=color,
                        opacity=0.8,
                        show_edges=True,
                        label=section_data['section_name']
                    )
                    
                    viewer.walls.append(wall_mesh)
                    viewer.wall_actors.append(actor)
            
            # Calculate and show intersections
            if show_intersections and len(viewer.walls) > 1:
                MultiSection3DViewer.calculate_section_intersections(viewer)
            
            # Add reference elements
            viewer.plotter.show_axes()
            viewer.plotter.add_axes()
            
            # Add ground plane if enabled
            if hasattr(viewer, 'show_plane_cb') and viewer.show_plane_cb.isChecked():
                MultiSection3DViewer.add_ground_plane(viewer, sections_data)
            
            viewer.plotter.reset_camera()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error adding polygon sections to 3D: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
    
    @staticmethod
    def create_section_wall(section_data, thickness, vertical_exag):
        """Create a 3D wall mesh from section data"""
        try:
            import pyvista as pv
            
            distances = section_data['distances']
            elevations = section_data['elevations'] * vertical_exag
            start_point = section_data['start']
            end_point = section_data['end']
            
            # Calculate direction vector
            dx = end_point.x() - start_point.x()
            dy = end_point.y() - start_point.y()
            length = np.sqrt(dx**2 + dy**2)
            
            if length == 0:
                return None
                
            # Normalize direction
            dx /= length
            dy /= length
            
            # Create points for the wall
            n_points = len(distances)
            points = []
            
            # Bottom and top points
            for i in range(n_points):
                # Calculate position along line
                ratio = distances[i] / section_data['total_distance']
                x = start_point.x() + ratio * (end_point.x() - start_point.x())
                y = start_point.y() + ratio * (end_point.y() - start_point.y())
                
                # Bottom point (ground level or min elevation)
                z_bottom = np.nanmin(elevations) - 10 * vertical_exag
                points.append([x, y, z_bottom])
                
            # Top points
            for i in range(n_points):
                ratio = distances[i] / section_data['total_distance']
                x = start_point.x() + ratio * (end_point.x() - start_point.x())
                y = start_point.y() + ratio * (end_point.y() - start_point.y())
                
                # Top point (actual elevation)
                z_top = elevations[i]
                points.append([x, y, z_top])
            
            # Create faces
            faces = []
            for i in range(n_points - 1):
                # Two triangles for each quad
                # Triangle 1
                faces.extend([3, i, i + n_points, i + n_points + 1])
                # Triangle 2
                faces.extend([3, i, i + n_points + 1, i + 1])
            
            # Create mesh
            mesh = pv.PolyData(np.array(points))
            mesh.faces = np.array(faces)
            
            # Add elevation scalar
            mesh['Elevation'] = np.concatenate([elevations, elevations])
            
            return mesh
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error creating section wall: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
            return None
    
    @staticmethod
    def calculate_section_intersections(viewer):
        """Calculate and display intersections between section walls"""
        try:
            import pyvista as pv
            
            n_walls = len(viewer.walls)
            intersections = []
            
            # Check each pair of walls
            for i in range(n_walls):
                for j in range(i + 1, n_walls):
                    try:
                        # Calculate intersection
                        intersection = viewer.walls[i].intersection(viewer.walls[j])
                        
                        if intersection and len(intersection.points) > 0:
                            # Add intersection as highlighted line
                            viewer.plotter.add_mesh(
                                intersection,
                                color='yellow',
                                line_width=5,
                                label=f'Intersection {i+1}-{j+1}'
                            )
                            intersections.append(intersection)
                            
                    except Exception as e:
                        continue
            
            QgsMessageLog.logMessage(f"Found {len(intersections)} wall intersections", 
                                   'DualProfileViewer', Qgis.Info)
                                   
        except Exception as e:
            QgsMessageLog.logMessage(f"Error calculating intersections: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
    
    @staticmethod
    def add_ground_plane(viewer, sections_data):
        """Add a ground reference plane"""
        try:
            import pyvista as pv
            
            # Get bounds from all sections
            all_x = []
            all_y = []
            all_z = []
            
            for section_data in sections_data:
                start = section_data['start']
                end = section_data['end']
                all_x.extend([start.x(), end.x()])
                all_y.extend([start.y(), end.y()])
                all_z.extend(section_data['elevations'])
            
            # Create plane at minimum elevation
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)
            z_min = np.nanmin(all_z) * (viewer.exag_slider.value() / 10.0)
            
            # Add some padding
            padding = 0.1 * max(x_max - x_min, y_max - y_min)
            
            plane = pv.Plane(
                center=((x_min + x_max) / 2, (y_min + y_max) / 2, z_min),
                direction=(0, 0, 1),
                i_size=(x_max - x_min) + 2 * padding,
                j_size=(y_max - y_min) + 2 * padding
            )
            
            viewer.plotter.add_mesh(
                plane,
                color='lightgray',
                opacity=0.3,
                label='Ground Plane'
            )
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error adding ground plane: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
    
    @staticmethod
    def export_polygon_sections_3d(viewer, sections_data, filename):
        """Export polygon sections as 3D model"""
        try:
            import pyvista as pv
            
            # Combine all walls into single mesh
            combined = pv.PolyData()
            
            for wall in viewer.walls:
                combined = combined + wall
            
            # Save based on extension
            if filename.endswith('.stl'):
                combined.save(filename)
            elif filename.endswith('.obj'):
                combined.save(filename)
            elif filename.endswith('.vtk'):
                combined.save(filename)
            else:
                # Default to STL
                combined.save(filename + '.stl')
                
            return True
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error exporting 3D model: {str(e)}", 
                                   'DualProfileViewer', Qgis.Critical)
            return False