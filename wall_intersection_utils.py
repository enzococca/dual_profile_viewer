# -*- coding: utf-8 -*-
"""
Utilities for calculating and visualizing wall intersections
"""

import numpy as np
from scipy.spatial import distance
import pyvista as pv

def find_wall_intersections(wall1_mesh, wall2_mesh, tolerance=1.0):
    """
    Find intersection between two wall meshes
    
    Args:
        wall1_mesh: PyVista mesh of first wall
        wall2_mesh: PyVista mesh of second wall
        tolerance: Distance tolerance for intersection
        
    Returns:
        intersection_line: PyVista PolyData of intersection
        intersection_points: Array of intersection points
    """
    try:
        # Get intersection using PyVista
        intersection = wall1_mesh.intersection(wall2_mesh)
        
        if intersection and len(intersection.points) > 0:
            # Sort points to form a continuous line
            points = intersection.points
            sorted_points = sort_points_along_line(points)
            
            # Create line from sorted points
            line = pv.PolyData()
            line.points = sorted_points
            cells = np.full((len(sorted_points)-1, 3), 2, dtype=np.int_)
            cells[:, 1] = np.arange(0, len(sorted_points)-1, dtype=np.int_)
            cells[:, 2] = np.arange(1, len(sorted_points), dtype=np.int_)
            line.lines = cells
            
            return line, sorted_points
        else:
            return None, None
            
    except Exception as e:
        print(f"Error finding intersection: {e}")
        return None, None

def sort_points_along_line(points):
    """
    Sort 3D points to form a continuous line
    
    Args:
        points: Array of 3D points
        
    Returns:
        sorted_points: Points sorted along the line
    """
    if len(points) < 2:
        return points
        
    # Start with the first point
    sorted_points = [points[0]]
    remaining = list(range(1, len(points)))
    
    # Greedily add closest points
    while remaining:
        last_point = sorted_points[-1]
        distances = [distance.euclidean(last_point, points[i]) for i in remaining]
        closest_idx = np.argmin(distances)
        sorted_points.append(points[remaining[closest_idx]])
        remaining.pop(closest_idx)
    
    return np.array(sorted_points)

def create_wall_from_profiles(top_profile, bottom_profile, thickness=None):
    """
    Create a 3D wall mesh from top and bottom profiles
    
    Args:
        top_profile: Dict with 'coordinates' and 'elevations'
        bottom_profile: Dict with 'coordinates' and 'elevations'
        thickness: Optional wall thickness (if None, uses actual bottom profile)
        
    Returns:
        wall_mesh: PyVista mesh of the wall
    """
    # Get coordinates
    if 'coordinates' in top_profile:
        top_coords = np.array(top_profile['coordinates'])
        if 'coordinates' in bottom_profile:
            bottom_coords = np.array(bottom_profile['coordinates'])
        else:
            bottom_coords = top_coords.copy()
    else:
        # Create coordinates from distances
        distances = np.array(top_profile['distances'])
        top_coords = np.column_stack([distances, np.zeros_like(distances)])
        bottom_coords = top_coords.copy()
    
    top_elevations = np.array(top_profile['elevations'])
    
    if thickness is not None:
        # Use uniform thickness
        bottom_elevations = top_elevations - thickness
    else:
        bottom_elevations = np.array(bottom_profile['elevations'])
    
    # Create points for the wall
    n_points = len(top_coords)
    points = []
    
    # Top surface points
    for i in range(n_points):
        points.append([top_coords[i][0], top_coords[i][1], top_elevations[i]])
    
    # Bottom surface points
    for i in range(n_points):
        points.append([bottom_coords[i][0], bottom_coords[i][1], bottom_elevations[i]])
    
    points = np.array(points)
    
    # Create faces
    faces = []
    
    # Wall faces (quads)
    for i in range(n_points - 1):
        face = [4, i, i+1, i+1+n_points, i+n_points]
        faces.extend(face)
    
    # End caps (triangles)
    # Start cap
    faces.extend([3, 0, n_points, n_points])
    # End cap
    faces.extend([3, n_points-1, 2*n_points-1, 2*n_points-1])
    
    # Create mesh
    mesh = pv.PolyData(points, faces)
    
    # Add scalar data
    mesh["Elevation"] = points[:, 2]
    mesh["ProfileID"] = np.concatenate([np.zeros(n_points), np.ones(n_points)])
    
    return mesh

def create_stratigraphic_layers(wall_mesh, layer_boundaries, layer_colors):
    """
    Create colored stratigraphic layers within a wall
    
    Args:
        wall_mesh: PyVista mesh of the wall
        layer_boundaries: List of elevation boundaries for layers
        layer_colors: List of colors for each layer
        
    Returns:
        layer_meshes: List of PyVista meshes for each layer
    """
    layer_meshes = []
    
    # Add elevation scalar if not present
    if "Elevation" not in wall_mesh.array_names:
        wall_mesh["Elevation"] = wall_mesh.points[:, 2]
    
    # Create each layer
    for i in range(len(layer_boundaries) - 1):
        lower_bound = layer_boundaries[i]
        upper_bound = layer_boundaries[i + 1]
        
        # Extract cells in this elevation range
        layer_mesh = wall_mesh.threshold(
            [lower_bound, upper_bound], 
            scalars="Elevation"
        )
        
        if layer_mesh.n_cells > 0:
            # Add layer ID for coloring
            layer_mesh["LayerID"] = i
            layer_meshes.append(layer_mesh)
    
    return layer_meshes

def calculate_intersection_angle(line1_points, line2_points):
    """
    Calculate the angle between two intersecting lines
    
    Args:
        line1_points: Points of first line
        line2_points: Points of second line
        
    Returns:
        angle: Angle in degrees
    """
    # Get direction vectors
    vec1 = line1_points[-1] - line1_points[0]
    vec2 = line2_points[-1] - line2_points[0]
    
    # Normalize
    vec1 = vec1 / np.linalg.norm(vec1)
    vec2 = vec2 / np.linalg.norm(vec2)
    
    # Calculate angle
    cos_angle = np.dot(vec1, vec2)
    angle = np.arccos(np.clip(cos_angle, -1, 1))
    
    return np.degrees(angle)

def create_intersection_marker(intersection_point, size=5.0, color='red'):
    """
    Create a marker for intersection points
    
    Args:
        intersection_point: 3D coordinates of intersection
        size: Marker size
        color: Marker color
        
    Returns:
        marker: PyVista sphere mesh
    """
    marker = pv.Sphere(radius=size, center=intersection_point)
    return marker