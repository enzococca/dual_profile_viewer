# -*- coding: utf-8 -*-
"""
Multi-Section Layout Extension
Handles layout generation for multiple polygon sections
"""

from qgis.core import (QgsLayoutItemLabel, QgsLayoutItemPicture, 
                      QgsLayoutItemMap, QgsLayoutPoint, QgsLayoutSize,
                      QgsUnitTypes, QgsTextFormat, QgsPalLayerSettings,
                      QgsMessageLog, Qgis)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont, QColor
import os
import tempfile

class MultiSectionLayoutGenerator:
    """Generate layouts for multiple polygon sections"""
    
    @staticmethod
    def add_multi_section_to_layout(layout, profile_data, start_y=50):
        """Add multiple sections to layout"""
        try:
            sections_data = profile_data.get('sections', [])
            n_sections = len(sections_data)
            
            if n_sections == 0:
                return start_y
            
            # Title
            title = QgsLayoutItemLabel(layout)
            title.setText(f"POLYGON SECTION ANALYSIS\n{n_sections} Sections")
            title.attemptMove(QgsLayoutPoint(105, start_y, QgsUnitTypes.LayoutMillimeters))
            title.attemptResize(QgsLayoutSize(190, 20, QgsUnitTypes.LayoutMillimeters))
            
            # Title formatting
            title_format = QgsTextFormat()
            title_font = QFont("Arial", 16)
            title_font.setBold(True)
            title_format.setFont(title_font)
            title_format.setSize(16)
            title_format.setSizeUnit(QgsUnitTypes.RenderPoints)
            title.setTextFormat(title_format)
            title.setHAlign(Qt.AlignCenter)
            
            layout.addLayoutItem(title)
            
            current_y = start_y + 25
            
            # Generate plot for all sections
            plot_path = MultiSectionLayoutGenerator.generate_multi_section_plot(
                sections_data, profile_data.get('dem1_name', 'DEM')
            )
            
            if plot_path and os.path.exists(plot_path):
                # Add plot image
                plot_item = QgsLayoutItemPicture(layout)
                plot_item.setPicturePath(plot_path)
                plot_item.attemptMove(QgsLayoutPoint(20, current_y, QgsUnitTypes.LayoutMillimeters))
                plot_item.attemptResize(QgsLayoutSize(260, 150, QgsUnitTypes.LayoutMillimeters))
                plot_item.setResizeMode(QgsLayoutItemPicture.Zoom)
                layout.addLayoutItem(plot_item)
                
                current_y += 160
            
            # Add statistics table
            current_y = MultiSectionLayoutGenerator.add_statistics_table(
                layout, sections_data, current_y
            )
            
            # Add section map if possible
            if 'polygon' in profile_data:
                current_y = MultiSectionLayoutGenerator.add_section_map(
                    layout, profile_data['polygon'], sections_data, current_y
                )
            
            return current_y + 20
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error adding multi-section to layout: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
            return start_y + 50
    
    @staticmethod
    def generate_multi_section_plot(sections_data, dem_name):
        """Generate plot image for multiple sections"""
        try:
            from .multi_section_handler import MultiSectionHandler
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            # Create figure using multi-section handler
            fig = MultiSectionHandler.create_matplotlib_multi_section(sections_data)
            
            if fig:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                fig.savefig(temp_file.name, dpi=300, bbox_inches='tight')
                plt.close(fig)
                return temp_file.name
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error generating multi-section plot: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
        
        return None
    
    @staticmethod
    def add_statistics_table(layout, sections_data, start_y):
        """Add statistics table for all sections"""
        try:
            from .multi_section_handler import MultiSectionHandler
            
            # Calculate statistics
            stats = MultiSectionHandler.calculate_multi_section_statistics(sections_data)
            
            # Create formatted text
            stats_text = "SECTION STATISTICS\n\n"
            
            # Overall stats
            if 'overall' in stats:
                overall = stats['overall']
                stats_text += f"Total Length: {overall['total_length']:.1f} m\n"
                stats_text += f"Overall Elevation Range: {overall['elevation_range']:.1f} m\n\n"
            
            # Individual sections (compact format)
            stats_text += "Individual Sections:\n"
            stats_text += "-" * 50 + "\n"
            stats_text += "Section | Length(m) | Min(m) | Max(m) | Mean(m)\n"
            stats_text += "-" * 50 + "\n"
            
            for key in sorted(stats.keys()):
                if key.startswith('section_'):
                    section = stats[key]
                    stats_text += f"{section['name']:8} | {section['length']:9.1f} | "
                    stats_text += f"{section['min_elevation']:6.1f} | "
                    stats_text += f"{section['max_elevation']:6.1f} | "
                    stats_text += f"{section['mean_elevation']:7.1f}\n"
            
            # Create text item
            stats_item = QgsLayoutItemLabel(layout)
            stats_item.setText(stats_text)
            stats_item.attemptMove(QgsLayoutPoint(20, start_y, QgsUnitTypes.LayoutMillimeters))
            stats_item.attemptResize(QgsLayoutSize(260, 80, QgsUnitTypes.LayoutMillimeters))
            
            # Format as monospace
            stats_format = QgsTextFormat()
            stats_font = QFont("Courier", 9)
            stats_format.setFont(stats_font)
            stats_format.setSize(9)
            stats_format.setSizeUnit(QgsUnitTypes.RenderPoints)
            stats_item.setTextFormat(stats_format)
            
            layout.addLayoutItem(stats_item)
            
            return start_y + 85
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error adding statistics table: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
            return start_y + 50
    
    @staticmethod
    def add_section_map(layout, polygon_geom, sections_data, start_y):
        """Add a map showing the polygon and sections"""
        try:
            # Create temporary layer with polygon
            from qgis.core import QgsVectorLayer, QgsFeature, QgsProject
            
            # Create memory layer
            layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Polygon Sections", "memory")
            provider = layer.dataProvider()
            
            # Add polygon feature
            feature = QgsFeature()
            feature.setGeometry(polygon_geom)
            provider.addFeature(feature)
            
            # Add to project temporarily
            QgsProject.instance().addMapLayer(layer, False)
            
            # Create map item
            map_item = QgsLayoutItemMap(layout)
            map_item.attemptMove(QgsLayoutPoint(20, start_y, QgsUnitTypes.LayoutMillimeters))
            map_item.attemptResize(QgsLayoutSize(100, 100, QgsUnitTypes.LayoutMillimeters))
            
            # Set extent to polygon
            map_item.setExtent(polygon_geom.boundingBox())
            map_item.setLayers([layer])
            
            layout.addLayoutItem(map_item)
            
            # Remove temporary layer
            QgsProject.instance().removeMapLayer(layer)
            
            return start_y + 105
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Error adding section map: {str(e)}", 
                                   'DualProfileViewer', Qgis.Warning)
            return start_y