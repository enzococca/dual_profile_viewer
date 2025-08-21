# -*- coding: utf-8 -*-
"""
Profile Exporter - Exports elevation profiles as georeferenced vectors
FIXED VERSION - Corrects polygon export issue
"""

from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPointXY, QgsLineString, QgsPoint,
    QgsField, QgsFields, QgsVectorFileWriter,
    QgsWkbTypes, QgsCoordinateReferenceSystem,
    QgsProject, QgsPolygon, QgsSingleSymbolRenderer,
    QgsSymbol, QgsSimpleLineSymbolLayer,
    QgsLineString
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface
import numpy as np
import math

class ProfileExporter:
    """Export elevation profiles as georeferenced vector geometries"""
    
    @staticmethod
    def export_profile_as_vector(profile_data, output_path, export_type='polyline', 
                                 scale_factor=1.0, vertical_exaggeration=1.0,
                                 baseline_offset=0.0, add_to_map=True):
        """
        Export profile as georeferenced vector maintaining the elevation shape
        """
        
        # Get CRS from project
        crs = QgsProject.instance().crs()
        
        # Create fields
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("profile", QVariant.String))
        fields.append(QgsField("type", QVariant.String))
        fields.append(QgsField("min_elev", QVariant.Double))
        fields.append(QgsField("max_elev", QVariant.Double))
        fields.append(QgsField("mean_elev", QVariant.Double))
        fields.append(QgsField("length_m", QVariant.Double))
        fields.append(QgsField("v_exag", QVariant.Double))
        fields.append(QgsField("scale", QVariant.Double))
        
        # Determine geometry type
        if export_type == 'polygon':
            geom_type = QgsWkbTypes.Polygon
            type_string = "Polygon"
        else:
            geom_type = QgsWkbTypes.LineString
            type_string = "LineString"
        
        # Create memory layer
        layer_name = "Profile_Vector_Export"
        layer = QgsVectorLayer(
            f"{type_string}?crs={crs.authid()}", 
            layer_name, 
            "memory"
        )
        
        provider = layer.dataProvider()
        provider.addAttributes(fields)
        layer.updateFields()
        
        # Process each profile
        profiles_to_export = []
        
        # Check if this is multi-section data
        if profile_data.get('multi_section', False):
            # Export multi-section data
            sections = profile_data.get('sections', [])
            colors = [QColor(255, 0, 0), QColor(0, 0, 255), QColor(0, 255, 0), 
                     QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255)]
            
            for idx, section in enumerate(sections):
                color = colors[idx % len(colors)]
                profiles_to_export.append({
                    'name': section.get('section_name', f'Section {idx + 1}'),
                    'profile': {
                        'distances': section['distances'],
                        'elevations': section['elevations'],
                        'x_coords': None,  # Will be calculated
                        'y_coords': None   # Will be calculated
                    },
                    'line': [section['start'], section['end']],
                    'color': color
                })
        else:
            # Profile 1 (A-A')
            if 'profile1' in profile_data and profile_data['profile1'] is not None:
                profiles_to_export.append({
                    'name': 'A-A\'',
                    'profile': profile_data['profile1'],
                    'line': profile_data['line1'],
                    'color': QColor(255, 0, 0)  # Red
                })
            
            # Profile 2 (B-B')  
            if 'profile2' in profile_data and profile_data['profile2'] is not None:
                profiles_to_export.append({
                    'name': 'B-B\'',
                    'profile': profile_data['profile2'],
                    'line': profile_data['line2'],
                    'color': QColor(0, 0, 255)  # Blue
                })
        
        features = []
        
        for idx, prof_info in enumerate(profiles_to_export):
            profile = prof_info['profile']
            line = prof_info['line']
            name = prof_info['name']
            
            # Create georeferenced profile geometry
            if export_type == 'polygon':
                geom = ProfileExporter._create_profile_polygon(
                    profile, line, scale_factor, vertical_exaggeration, baseline_offset
                )
            else:
                geom = ProfileExporter._create_profile_polyline(
                    profile, line, scale_factor, vertical_exaggeration, baseline_offset
                )
            
            if geom and geom.isGeosValid():
                # Calculate statistics
                elevations = profile['elevations']
                valid_elevs = elevations[~np.isnan(elevations)]
                
                # Create feature
                feature = QgsFeature()
                feature.setGeometry(geom)
                feature.setAttributes([
                    idx + 1,
                    name,
                    export_type,
                    float(np.min(valid_elevs)) if len(valid_elevs) > 0 else 0.0,
                    float(np.max(valid_elevs)) if len(valid_elevs) > 0 else 0.0,
                    float(np.mean(valid_elevs)) if len(valid_elevs) > 0 else 0.0,
                    float(profile['distances'][-1]),
                    vertical_exaggeration,
                    scale_factor
                ])
                features.append(feature)
        
        # Add features to layer
        provider.addFeatures(features)
        
        # Apply symbology
        ProfileExporter._apply_symbology(layer, export_type)
        
        # Save to file if path provided
        if output_path:
            save_options = QgsVectorFileWriter.SaveVectorOptions()
            save_options.driverName = "GPKG" if output_path.endswith('.gpkg') else "ESRI Shapefile"
            save_options.fileEncoding = "UTF-8"
            
            error = QgsVectorFileWriter.writeAsVectorFormatV2(
                layer, output_path, QgsProject.instance().transformContext(), save_options
            )
            
            if error[0] != QgsVectorFileWriter.NoError:
                raise Exception(f"Error saving file: {error[1]}")
        
        # Add to map if requested
        if add_to_map:
            # Load the saved file as a new layer
            map_layer = QgsVectorLayer(output_path, layer_name, "ogr")
            if map_layer.isValid():
                QgsProject.instance().addMapLayer(map_layer)
                # Zoom to layer extent
                iface.mapCanvas().setExtent(map_layer.extent())
                iface.mapCanvas().refresh()
            else:
                # Fallback to clone method
                map_layer = layer.clone()
                map_layer.setName(layer_name)
                QgsProject.instance().addMapLayer(map_layer)
        
        return layer
    
    @staticmethod
    def _create_profile_polyline(profile, line, scale_factor=1.0, 
                                 vertical_exaggeration=1.0, baseline_offset=0.0):
        """
        Create a polyline following the elevation profile shape
        Projects the elevation perpendicular to the profile line
        """
        # Get line start and end points
        start_point = line[0]
        end_point = line[1]
        
        # Calculate line direction
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        line_length = math.sqrt(dx*dx + dy*dy)
        
        if line_length == 0:
            return None
        
        # Unit vector along line
        ux = dx / line_length
        uy = dy / line_length
        
        # Perpendicular unit vector (for elevation offset)
        # Rotate 90 degrees counter-clockwise
        px = -uy
        py = ux
        
        # Create points for the profile
        points = []
        
        # Find minimum elevation for baseline reference
        valid_elevs = profile['elevations'][~np.isnan(profile['elevations'])]
        if len(valid_elevs) == 0:
            return None
        
        min_elev = np.min(valid_elevs)
        
        for i in range(len(profile['distances'])):
            if not np.isnan(profile['elevations'][i]):
                # Position along the line (interpolated)
                if profile['distances'][-1] > 0:
                    dist_ratio = profile['distances'][i] / profile['distances'][-1]
                else:
                    dist_ratio = 0
                
                # Base position along the profile line
                x_base = start_point.x() + dx * dist_ratio
                y_base = start_point.y() + dy * dist_ratio
                
                # Calculate elevation offset from baseline
                # This creates the "height" of the profile
                elev_diff = profile['elevations'][i] - min_elev
                elev_offset = (elev_diff * vertical_exaggeration + baseline_offset) * scale_factor
                
                # Apply perpendicular offset for elevation
                # This projects the elevation perpendicular to the profile line
                x_final = x_base + px * elev_offset
                y_final = y_base + py * elev_offset
                
                points.append(QgsPoint(x_final, y_final))
        
        if len(points) > 1:
            line_string = QgsLineString(points)
            return QgsGeometry(line_string)
        
        return None
    
    @staticmethod
    def _create_profile_polygon(profile, line, scale_factor=1.0, 
                                vertical_exaggeration=1.0, baseline_offset=0.0):
        """
        FIXED VERSION - Create a polygon representing the profile area
        The polygon extends from the baseline to the elevation profile
        """
        # Get line start and end points
        start_point = line[0]
        end_point = line[1]
        
        # Calculate line direction
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        line_length = math.sqrt(dx*dx + dy*dy)
        
        if line_length == 0:
            return None
        
        # Unit vectors
        ux = dx / line_length
        uy = dy / line_length
        px = -uy  # perpendicular
        py = ux
        
        # Filter out NaN values first
        valid_indices = []
        for i in range(len(profile['elevations'])):
            if not np.isnan(profile['elevations'][i]):
                valid_indices.append(i)
        
        if len(valid_indices) < 2:
            return None
        
        # Get valid elevations
        valid_elevs = profile['elevations'][valid_indices]
        min_elev = np.min(valid_elevs)
        
        # Create polygon points - only for valid elevation points
        polygon_points = []
        
        # First, add all top points (with elevation) from start to end
        for i in valid_indices:
            # Position along the line
            if profile['distances'][-1] > 0:
                dist_ratio = profile['distances'][i] / profile['distances'][-1]
            else:
                dist_ratio = 0
                
            x_base = start_point.x() + dx * dist_ratio
            y_base = start_point.y() + dy * dist_ratio
            
            # Top point (with elevation)
            elev_diff = profile['elevations'][i] - min_elev
            elev_offset = (elev_diff * vertical_exaggeration + baseline_offset) * scale_factor
            x_top = x_base + px * elev_offset
            y_top = y_base + py * elev_offset
            polygon_points.append(QgsPoint(x_top, y_top))
        
        # Then add all bottom points (baseline) from end to start (reversed)
        for i in reversed(valid_indices):
            # Position along the line
            if profile['distances'][-1] > 0:
                dist_ratio = profile['distances'][i] / profile['distances'][-1]
            else:
                dist_ratio = 0
                
            x_base = start_point.x() + dx * dist_ratio
            y_base = start_point.y() + dy * dist_ratio
            
            # Bottom point (baseline with small offset)
            x_bottom = x_base + px * baseline_offset * scale_factor
            y_bottom = y_base + py * baseline_offset * scale_factor
            polygon_points.append(QgsPoint(x_bottom, y_bottom))
        
        # Close the polygon by adding the first point again
        if len(polygon_points) > 0:
            polygon_points.append(polygon_points[0])
        
        # Create the polygon
        if len(polygon_points) > 3:  # Need at least 4 points for a valid polygon (including closing point)
            try:
                # Create QgsLineString from points
                line_string = QgsLineString()
                for point in polygon_points:
                    line_string.addVertex(point)
                
                # Create polygon
                polygon = QgsPolygon()
                polygon.setExteriorRing(line_string)
                
                # Create geometry
                geom = QgsGeometry(polygon)
                
                # Validate geometry
                if not geom.isGeosValid():
                    # Try to fix invalid geometry
                    geom = geom.buffer(0, 1)
                
                return geom
                
            except Exception as e:
                print(f"Error creating polygon: {e}")
                return None
        
        return None
    
    @staticmethod
    def _apply_symbology(layer, geom_type):
        """Apply symbology to the exported layer"""
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        
        if geom_type == 'polygon':
            # Semi-transparent fill with solid border
            symbol.setColor(QColor(100, 150, 200, 100))
            if symbol.symbolLayer(0):
                symbol.symbolLayer(0).setStrokeColor(QColor(50, 100, 150))
                symbol.symbolLayer(0).setStrokeWidth(0.5)
        else:
            # Solid line
            symbol.setColor(QColor(200, 50, 50))
            symbol.setWidth(1.0)
        
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
    
    @staticmethod
    def export_profiles_as_3d_vector(profile_data, output_path, add_to_map=True):
        """
        Export profiles as 3D polylines with real elevations
        """
        crs = QgsProject.instance().crs()
        
        # Create 3D layer
        layer = QgsVectorLayer(
            f"LineStringZ?crs={crs.authid()}", 
            "Profile_3D", 
            "memory"
        )
        
        # Add fields
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("profile", QVariant.String))
        fields.append(QgsField("length_m", QVariant.Double))
        fields.append(QgsField("min_z", QVariant.Double))
        fields.append(QgsField("max_z", QVariant.Double))
        
        provider = layer.dataProvider()
        provider.addAttributes(fields)
        layer.updateFields()
        
        features = []
        feature_id = 1
        
        # Export each profile as 3D line
        for name, profile_key in [('A-A\'', 'profile1'), ('B-B\'', 'profile2')]:
            if profile_key in profile_data and profile_data[profile_key] is not None:
                profile = profile_data[profile_key]
                
                # Create 3D points
                points_3d = []
                valid_z = []
                
                for i in range(len(profile['x_coords'])):
                    if not np.isnan(profile['elevations'][i]):
                        point_3d = QgsPoint(
                            profile['x_coords'][i],
                            profile['y_coords'][i],
                            profile['elevations'][i]
                        )
                        points_3d.append(point_3d)
                        valid_z.append(profile['elevations'][i])
                
                if len(points_3d) > 1:
                    line_3d = QgsLineString(points_3d)
                    
                    feature = QgsFeature()
                    feature.setGeometry(QgsGeometry(line_3d))
                    feature.setAttributes([
                        feature_id,
                        name,
                        float(profile['distances'][-1]),
                        float(np.min(valid_z)),
                        float(np.max(valid_z))
                    ])
                    features.append(feature)
                    feature_id += 1
        
        provider.addFeatures(features)
        
        # Save to file
        if output_path:
            save_options = QgsVectorFileWriter.SaveVectorOptions()
            save_options.driverName = "GPKG" if output_path.endswith('.gpkg') else "ESRI Shapefile"
            
            QgsVectorFileWriter.writeAsVectorFormatV2(
                layer, output_path, 
                QgsProject.instance().transformContext(),
                save_options
            )
        
        # Add to map
        if add_to_map:
            QgsProject.instance().addMapLayer(layer)
        
        return layer