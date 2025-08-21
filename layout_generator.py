# -*- coding: utf-8 -*-
"""
Professional Layout Generator for Dual Profile Viewer
Creates print-ready layouts with 2D profiles, 3D views, and statistics
"""

from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QRectF, QSizeF, Qt
from qgis.PyQt.QtGui import QFont, QColor
from qgis.core import (
    QgsProject, QgsLayout, QgsLayoutItemMap, QgsLayoutItemLabel,
    QgsLayoutItemPicture, QgsLayoutItemScaleBar, QgsLayoutItemLegend,
    QgsLayoutItemShape, QgsLayoutPoint, QgsLayoutSize,
    QgsUnitTypes, QgsLayoutItemPage, QgsLayoutItemPolyline,
    QgsLayoutItemTextTable, QgsRectangle, QgsLayoutFrame,
    QgsLayoutMultiFrame, QgsTextFormat, QgsMapSettings,
    QgsPrintLayout, QgsReadWriteContext, QgsLayoutExporter,
    QgsMapRendererJob, QgsLayoutMeasurement, QgsLayoutTable,
    QgsGeometry
)
import tempfile
import os

class LayoutGenerator:
    """Generate professional layouts for profile analysis"""
    
    def __init__(self, iface):
        self.iface = iface
        self.layout = None
        
    def create_profile_layout(self, profile_data, plot_image_path=None, view_3d_image_path=None, all_sections=None, ai_report_text=None):
        """Create a professional layout with all profile data"""
        
        # Create new print layout
        project = QgsProject.instance()
        layout_name = f"Profile Analysis - {profile_data.get('dem1_name', 'DEM')}"
        
        # Remove existing layout with same name
        existing = project.layoutManager().layoutByName(layout_name)
        if existing:
            project.layoutManager().removeLayout(existing)
        
        # Create new layout
        self.layout = QgsPrintLayout(project)
        self.layout.initializeDefaults()
        self.layout.setName(layout_name)
        
        # Get all sections to show
        sections_to_show = []
        if all_sections:
            sections_to_show = all_sections
        elif profile_data:
            # Create a section entry for current data
            sections_to_show = [{
                'profile_data': profile_data,
                'plot_image': plot_image_path,
                'section_number': 1
            }]
        
        # Create one page per section
        for idx, section in enumerate(sections_to_show):
            if idx == 0:
                # Use existing first page
                page = self.layout.pageCollection().page(0)
            else:
                # Add new page
                page = QgsLayoutItemPage(self.layout)
                self.layout.pageCollection().addPage(page)
            
            page.setPageSize('A3', QgsLayoutItemPage.Landscape)
            
            # Add section content
            self.create_section_page_new(section, page_number=idx)
        
        # Add AI report page if available
        if ai_report_text:
            self.add_ai_report_page(ai_report_text)
        
        # Add to project
        project.layoutManager().addLayout(self.layout)
        
        return self.layout
        
    def add_title(self, profile_data):
        """Add professional title block"""
        # Main title
        title = QgsLayoutItemLabel(self.layout)
        title.setText("ARCHAEOLOGICAL PROFILE ANALYSIS")
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.attemptMove(QgsLayoutPoint(20, 10, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(380, 15, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(title)
        
        # Subtitle with DEM info
        subtitle = QgsLayoutItemLabel(self.layout)
        subtitle.setText(f"Primary DEM: {profile_data.get('dem1_name', 'Unknown')}")
        subtitle.setFont(QFont('Arial', 12))
        subtitle.attemptMove(QgsLayoutPoint(20, 25, QgsUnitTypes.LayoutMillimeters))
        subtitle.attemptResize(QgsLayoutSize(380, 10, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(subtitle)
        
        # Date
        from datetime import datetime
        date_label = QgsLayoutItemLabel(self.layout)
        date_label.setText(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        date_label.setFont(QFont('Arial', 10))
        date_label.attemptMove(QgsLayoutPoint(20, 35, QgsUnitTypes.LayoutMillimeters))
        date_label.attemptResize(QgsLayoutSize(100, 8, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(date_label)
        
    def add_main_map(self, profile_data):
        """Add main map showing section lines"""
        map_item = QgsLayoutItemMap(self.layout)
        map_item.setId('map1')  # Set ID for scale bar reference
        map_item.attemptMove(QgsLayoutPoint(20, 50, QgsUnitTypes.LayoutMillimeters))
        map_item.attemptResize(QgsLayoutSize(180, 130, QgsUnitTypes.LayoutMillimeters))
        
        # Set extent to show section lines
        extent = None
        
        if profile_data.get('multi_section', False):
            # Multi-section mode - use polygon extent
            if 'polygon' in profile_data:
                extent = profile_data['polygon'].boundingBox()
        else:
            # Regular profile mode
            if 'line1' in profile_data and profile_data['line1'] is not None:
                all_points = []
                # Get points from line1
                if isinstance(profile_data['line1'], QgsGeometry):
                    all_points.extend(profile_data['line1'].asPolyline())
                elif isinstance(profile_data['line1'], list):
                    all_points.extend(profile_data['line1'])
                
                # Get points from line2 if available
                if 'line2' in profile_data and profile_data['line2'] is not None:
                    if isinstance(profile_data['line2'], QgsGeometry):
                        all_points.extend(profile_data['line2'].asPolyline())
                    elif isinstance(profile_data['line2'], list):
                        all_points.extend(profile_data['line2'])
                
                if all_points:
                    x_coords = [p.x() for p in all_points]
                    y_coords = [p.y() for p in all_points]
                    
                    extent = QgsRectangle(
                        min(x_coords), min(y_coords),
                        max(x_coords), max(y_coords)
                    )
        
        if extent:
            # Add 10% buffer
            extent.scale(1.1)
            map_item.setExtent(extent)
        else:
            # Use current canvas extent
            map_item.setExtent(self.iface.mapCanvas().extent())
        
        map_item.setFrameEnabled(True)
        map_item.setFrameStrokeWidth(QgsLayoutMeasurement(1, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(map_item)
        
        # Add map title
        map_title = QgsLayoutItemLabel(self.layout)
        map_title.setText("Section Location Map")
        map_title.setFont(QFont('Arial', 11, QFont.Bold))
        map_title.attemptMove(QgsLayoutPoint(20, 45, QgsUnitTypes.LayoutMillimeters))
        map_title.attemptResize(QgsLayoutSize(180, 8, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(map_title)
        
        return map_item  # Return for scale bar reference
        
    def add_profile_plots(self, plot_image_path):
        """Add profile plots image"""
        if not plot_image_path or not os.path.exists(plot_image_path):
            # Add placeholder text if no image
            placeholder = QgsLayoutItemLabel(self.layout)
            placeholder.setText("Profile Plots\n\n[Plots could not be generated automatically.\nPlease add manually or use matplotlib view.]")
            placeholder.setFont(QFont('Arial', 10))
            placeholder.attemptMove(QgsLayoutPoint(210, 80, QgsUnitTypes.LayoutMillimeters))
            placeholder.attemptResize(QgsLayoutSize(180, 100, QgsUnitTypes.LayoutMillimeters))
            placeholder.setFrameEnabled(True)
            placeholder.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
            placeholder.setHorizontalAlignment(Qt.AlignCenter)
            placeholder.setVerticalAlignment(Qt.AlignVCenter)
            self.layout.addLayoutItem(placeholder)
            return
            
        picture = QgsLayoutItemPicture(self.layout)
        picture.setPicturePath(plot_image_path)
        picture.attemptMove(QgsLayoutPoint(210, 50, QgsUnitTypes.LayoutMillimeters))
        picture.attemptResize(QgsLayoutSize(180, 130, QgsUnitTypes.LayoutMillimeters))
        picture.setFrameEnabled(True)
        picture.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(picture)
        
        # Add title
        plot_title = QgsLayoutItemLabel(self.layout)
        plot_title.setText("Elevation Profiles")
        plot_title.setFont(QFont('Arial', 11, QFont.Bold))
        plot_title.attemptMove(QgsLayoutPoint(210, 45, QgsUnitTypes.LayoutMillimeters))
        plot_title.attemptResize(QgsLayoutSize(180, 8, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(plot_title)
        
    def add_3d_view(self, view_3d_image_path):
        """Add 3D view image"""
        if not os.path.exists(view_3d_image_path):
            return
            
        picture = QgsLayoutItemPicture(self.layout)
        picture.setPicturePath(view_3d_image_path)
        picture.attemptMove(QgsLayoutPoint(20, 195, QgsUnitTypes.LayoutMillimeters))
        picture.attemptResize(QgsLayoutSize(180, 85, QgsUnitTypes.LayoutMillimeters))
        picture.setFrameEnabled(True)
        picture.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(picture)
        
        # Add title
        view_title = QgsLayoutItemLabel(self.layout)
        view_title.setText("3D Geological View")
        view_title.setFont(QFont('Arial', 11, QFont.Bold))
        view_title.attemptMove(QgsLayoutPoint(20, 190, QgsUnitTypes.LayoutMillimeters))
        view_title.attemptResize(QgsLayoutSize(180, 8, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(view_title)
        
    def add_statistics_table(self, profile_data):
        """Add statistics table"""
        # Create a simple table using labels instead of QgsLayoutItemTextTable
        import numpy as np
        
        # Calculate statistics
        profile1 = profile_data['profile1']
        profile2 = profile_data.get('profile2')
        single_mode = profile_data.get('single_mode', False) or profile2 is None
        
        # Create table as formatted text
        table_text = "STATISTICAL SUMMARY\n\n"
        table_text += "-" * 80 + "\n"
        
        if single_mode:
            # Single profile statistics
            table_text += f"{'Parameter':<25} {'Value':>15}\n"
            table_text += "-" * 80 + "\n"
            
            # Min elevation
            min1 = np.nanmin(profile1['elevations'])
            table_text += f"{'Min Elevation (m)':<25} {min1:>15.2f}\n"
            
            # Max elevation
            max1 = np.nanmax(profile1['elevations'])
            table_text += f"{'Max Elevation (m)':<25} {max1:>15.2f}\n"
            
            # Mean elevation
            mean1 = np.nanmean(profile1['elevations'])
            table_text += f"{'Mean Elevation (m)':<25} {mean1:>15.2f}\n"
            
            # Length
            len1 = profile1['distances'][-1]
            table_text += f"{'Length (m)':<25} {len1:>15.2f}\n"
            
        else:
            # Dual profile statistics
            profile_a_label = "Profile A-A'"
            profile_b_label = "Profile B-B'"
            table_text += f"{'Parameter':<25} {profile_a_label:>15} {profile_b_label:>15} {'Difference':>15}\n"
            table_text += "-" * 80 + "\n"
            
            # Min elevation
            min1 = np.nanmin(profile1['elevations'])
            min2 = np.nanmin(profile2['elevations'])
            table_text += f"{'Min Elevation (m)':<25} {min1:>15.2f} {min2:>15.2f} {(min1-min2):>15.2f}\n"
            
            # Max elevation
            max1 = np.nanmax(profile1['elevations'])
            max2 = np.nanmax(profile2['elevations'])
            table_text += f"{'Max Elevation (m)':<25} {max1:>15.2f} {max2:>15.2f} {(max1-max2):>15.2f}\n"
            
            # Mean elevation
            mean1 = np.nanmean(profile1['elevations'])
            mean2 = np.nanmean(profile2['elevations'])
            table_text += f"{'Mean Elevation (m)':<25} {mean1:>15.2f} {mean2:>15.2f} {(mean1-mean2):>15.2f}\n"
            
            # Length
            len1 = profile1['distances'][-1]
            len2 = profile2['distances'][-1]
            table_text += f"{'Length (m)':<25} {len1:>15.2f} {len2:>15.2f} {'-':>15}\n"
        
        table_text += "-" * 80 + "\n"
        
        # Add comparison DEM stats if available
        if profile_data.get('profile1_dem2'):
            table_text += "\nCOMPARISON DEM: " + profile_data.get('dem2_name', 'DEM2') + "\n"
            table_text += "-" * 80 + "\n"
            
            profile1_dem2 = profile_data['profile1_dem2']
            profile2_dem2 = profile_data.get('profile2_dem2')
            
            if single_mode:
                min1_2 = np.nanmin(profile1_dem2['elevations'])
                table_text += f"{'Min Elevation (m)':<25} {min1_2:>15.2f}\n"
                
                max1_2 = np.nanmax(profile1_dem2['elevations'])
                table_text += f"{'Max Elevation (m)':<25} {max1_2:>15.2f}\n"
            else:
                min1_2 = np.nanmin(profile1_dem2['elevations'])
                min2_2 = np.nanmin(profile2_dem2['elevations']) if profile2_dem2 else 0
                table_text += f"{'Min Elevation (m)':<25} {min1_2:>15.2f} {min2_2:>15.2f} {(min1_2-min2_2):>15.2f}\n"
                
                max1_2 = np.nanmax(profile1_dem2['elevations'])
                max2_2 = np.nanmax(profile2_dem2['elevations']) if profile2_dem2 else 0
                table_text += f"{'Max Elevation (m)':<25} {max1_2:>15.2f} {max2_2:>15.2f} {(max1_2-max2_2):>15.2f}\n"
            
            table_text += "-" * 80 + "\n"
        
        # Create label for table
        table_label = QgsLayoutItemLabel(self.layout)
        table_label.setText(table_text)
        table_label.setFont(QFont('Courier', 8))  # Use monospace font
        table_label.attemptMove(QgsLayoutPoint(210, 190, QgsUnitTypes.LayoutMillimeters))
        table_label.attemptResize(QgsLayoutSize(180, 80, QgsUnitTypes.LayoutMillimeters))
        table_label.setFrameEnabled(True)
        table_label.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
        table_label.setMarginX(5)
        table_label.setMarginY(5)
        self.layout.addLayoutItem(table_label)
        
        # Stats title is already included in the table text above
        
    def add_scale_bar(self):
        """Add scale bar"""
        scale_bar = QgsLayoutItemScaleBar(self.layout)
        scale_bar.setStyle('Single Box')
        scale_bar.setUnits(QgsUnitTypes.DistanceMeters)
        scale_bar.setNumberOfSegments(4)
        scale_bar.setNumberOfSegmentsLeft(0)
        
        # Link to map1
        map1 = self.layout.itemById('map1')
        if map1:
            scale_bar.setLinkedMap(map1)
            # Calculate appropriate scale based on map extent
            extent = map1.extent()
            width = extent.width()
            # Calculate nice round number for scale
            scale_width = width / 4  # Roughly 1/4 of map width
            if scale_width > 1000:
                scale_bar.setUnitsPerSegment(round(scale_width / 1000) * 250)  # Round to 250m
            elif scale_width > 100:
                scale_bar.setUnitsPerSegment(round(scale_width / 100) * 25)  # Round to 25m
            else:
                scale_bar.setUnitsPerSegment(round(scale_width / 10) * 5)  # Round to 5m
        
        # Position under map1
        scale_bar.attemptMove(QgsLayoutPoint(20, 182, QgsUnitTypes.LayoutMillimeters))
        scale_bar.attemptResize(QgsLayoutSize(80, 8, QgsUnitTypes.LayoutMillimeters))
        scale_bar.setFrameEnabled(False)
        self.layout.addLayoutItem(scale_bar)
        
    def add_north_arrow(self):
        """Add north arrow"""
        north_arrow = QgsLayoutItemPicture(self.layout)
        # Use QGIS default north arrow
        north_arrow.setPicturePath(':/images/north_arrows/layout_default_north_arrow.svg')
        # Position near top right of map1
        north_arrow.attemptMove(QgsLayoutPoint(185, 55, QgsUnitTypes.LayoutMillimeters))
        north_arrow.attemptResize(QgsLayoutSize(12, 15, QgsUnitTypes.LayoutMillimeters))
        north_arrow.setFrameEnabled(False)
        self.layout.addLayoutItem(north_arrow)
        
    def add_legend(self):
        """Add legend"""
        legend = QgsLayoutItemLegend(self.layout)
        legend.setTitle("Legend")
        # Position on the right side in empty space
        legend.attemptMove(QgsLayoutPoint(340, 100, QgsUnitTypes.LayoutMillimeters))
        legend.attemptResize(QgsLayoutSize(50, 60, QgsUnitTypes.LayoutMillimeters))
        legend.setFrameEnabled(True)
        legend.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
        # Link to map1 for automatic legend items
        map1 = self.layout.itemById('map1')
        if map1:
            legend.setLinkedMap(map1)
        self.layout.addLayoutItem(legend)
        
    def add_metadata(self, profile_data):
        """Add metadata box"""
        # Create metadata text
        metadata_text = f"""Project: {QgsProject.instance().title() or 'Untitled'}
CRS: {QgsProject.instance().crs().authid()}
Primary DEM: {profile_data.get('dem1_name', 'Unknown')}
Comparison DEM: {profile_data.get('dem2_name', 'None')}
Offset: {profile_data.get('offset', 0)} m
Analysis by: Dual Profile Viewer Plugin"""
        
        metadata = QgsLayoutItemLabel(self.layout)
        metadata.setText(metadata_text)
        metadata.setFont(QFont('Arial', 8))
        # Position in bottom right area
        metadata.attemptMove(QgsLayoutPoint(320, 240, QgsUnitTypes.LayoutMillimeters))
        metadata.attemptResize(QgsLayoutSize(80, 45, QgsUnitTypes.LayoutMillimeters))
        metadata.setFrameEnabled(True)
        metadata.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
        metadata.setMarginX(2)
        metadata.setMarginY(2)
        self.layout.addLayoutItem(metadata)
        
    def add_grid_references(self):
        """Add coordinate grid references"""
        # Add border rectangle FIRST (so it's under everything)
        border = QgsLayoutItemShape(self.layout)
        border.setShapeType(QgsLayoutItemShape.Rectangle)
        border.attemptMove(QgsLayoutPoint(10, 40, QgsUnitTypes.LayoutMillimeters))
        border.attemptResize(QgsLayoutSize(400, 250, QgsUnitTypes.LayoutMillimeters))
        border.setFrameEnabled(True)
        border.setFrameStrokeWidth(QgsLayoutMeasurement(1, QgsUnitTypes.LayoutMillimeters))
        border.setFrameStrokeColor(QColor(0, 0, 0))
        # Send to back
        border.setZValue(-1)
        self.layout.addLayoutItem(border)
    
    def create_section_page_new(self, section_data, page_number):
        """Create a single page for one section with new layout"""
        y_offset = page_number * 297  # A3 height in mm
        
        # Add page border
        border = QgsLayoutItemShape(self.layout)
        border.setShapeType(QgsLayoutItemShape.Rectangle)
        border.attemptMove(QgsLayoutPoint(10, 10 + y_offset, QgsUnitTypes.LayoutMillimeters))
        border.attemptResize(QgsLayoutSize(400, 277, QgsUnitTypes.LayoutMillimeters))
        border.setFrameEnabled(True)
        border.setFrameStrokeWidth(QgsLayoutMeasurement(1, QgsUnitTypes.LayoutMillimeters))
        border.setFrameStrokeColor(QColor(0, 0, 0))
        self.layout.addLayoutItem(border)
        
        profile_data = section_data['profile_data']
        section_num = section_data.get('section_number', page_number + 1)
        
        # Title
        title = QgsLayoutItemLabel(self.layout)
        title_text = f"SECTION {section_num} ANALYSIS"
        if profile_data.get('single_mode'):
            title_text += " - SINGLE PROFILE"
        title.setText(title_text)
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.attemptMove(QgsLayoutPoint(20, 20 + y_offset, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(380, 15, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(title)
        
        # Map showing section location (right side)
        map_item = QgsLayoutItemMap(self.layout)
        map_item.setId(f'map_{page_number}')
        map_item.attemptMove(QgsLayoutPoint(220, 40 + y_offset, QgsUnitTypes.LayoutMillimeters))
        map_item.attemptResize(QgsLayoutSize(180, 130, QgsUnitTypes.LayoutMillimeters))
        
        # Set extent based on section lines
        self.set_map_extent_for_section(map_item, profile_data)
        
        map_item.setFrameEnabled(True)
        map_item.setFrameStrokeWidth(QgsLayoutMeasurement(1, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(map_item)
        
        # Map title
        map_title = QgsLayoutItemLabel(self.layout)
        map_title.setText("Section Location")
        map_title.setFont(QFont('Arial', 11, QFont.Bold))
        map_title.attemptMove(QgsLayoutPoint(220, 35 + y_offset, QgsUnitTypes.LayoutMillimeters))
        map_title.attemptResize(QgsLayoutSize(180, 8, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(map_title)
        
        # Profile plot (left side)
        if section_data.get('plot_image') and os.path.exists(section_data['plot_image']):
            plot_item = QgsLayoutItemPicture(self.layout)
            plot_item.setPicturePath(section_data['plot_image'])
            plot_item.attemptMove(QgsLayoutPoint(20, 40 + y_offset, QgsUnitTypes.LayoutMillimeters))
            plot_item.attemptResize(QgsLayoutSize(190, 130, QgsUnitTypes.LayoutMillimeters))
            plot_item.setFrameEnabled(True)
            plot_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
            self.layout.addLayoutItem(plot_item)
        
        # Statistics table (below map)
        self.add_section_statistics(profile_data, 220, 180 + y_offset)
        
        # Scale bar adapted to section
        scale_bar = QgsLayoutItemScaleBar(self.layout)
        scale_bar.setStyle('Single Box')
        scale_bar.setUnits(QgsUnitTypes.DistanceMeters)
        scale_bar.setNumberOfSegments(4)
        scale_bar.setNumberOfSegmentsLeft(0)
        scale_bar.setLinkedMap(map_item)
        
        # Auto-calculate scale based on section length
        self.set_adaptive_scale(scale_bar, profile_data)
        
        scale_bar.attemptMove(QgsLayoutPoint(220, 172 + y_offset, QgsUnitTypes.LayoutMillimeters))
        scale_bar.attemptResize(QgsLayoutSize(80, 8, QgsUnitTypes.LayoutMillimeters))
        scale_bar.setFrameEnabled(False)
        self.layout.addLayoutItem(scale_bar)
        
        # North arrow
        north_arrow = QgsLayoutItemPicture(self.layout)
        north_arrow.setPicturePath(':/images/north_arrows/layout_default_north_arrow.svg')
        north_arrow.attemptMove(QgsLayoutPoint(385, 45 + y_offset, QgsUnitTypes.LayoutMillimeters))
        north_arrow.attemptResize(QgsLayoutSize(12, 15, QgsUnitTypes.LayoutMillimeters))
        north_arrow.setFrameEnabled(False)
        self.layout.addLayoutItem(north_arrow)
        
        # Additional info below profile
        info_text = self.create_section_info_text(profile_data)
        info_label = QgsLayoutItemLabel(self.layout)
        info_label.setText(info_text)
        info_label.setFont(QFont('Arial', 9))
        info_label.attemptMove(QgsLayoutPoint(20, 175 + y_offset, QgsUnitTypes.LayoutMillimeters))
        info_label.attemptResize(QgsLayoutSize(190, 100, QgsUnitTypes.LayoutMillimeters))
        info_label.setFrameEnabled(True)
        info_label.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
        info_label.setMarginX(5)
        info_label.setMarginY(5)
        self.layout.addLayoutItem(info_label)
        
    def export_layout(self, output_path, format='PDF'):
        """Export the layout to file"""
        if not self.layout:
            return False
            
        exporter = QgsLayoutExporter(self.layout)
        
        if format.upper() == 'PDF':
            settings = QgsLayoutExporter.PdfExportSettings()
            settings.dpi = 300
            result = exporter.exportToPdf(output_path, settings)
        elif format.upper() == 'PNG':
            settings = QgsLayoutExporter.ImageExportSettings()
            settings.dpi = 300
            result = exporter.exportToImage(output_path, settings)
        else:
            return False
            
        return result == QgsLayoutExporter.Success
    
    def set_map_extent_for_section(self, map_item, profile_data):
        """Set map extent based on section data"""
        extent = None
        
        if profile_data.get('multi_section'):
            # Multi-section - use polygon extent
            if 'polygon' in profile_data:
                extent = profile_data['polygon'].boundingBox()
        else:
            # Regular section
            all_points = []
            if 'line1' in profile_data and profile_data['line1'] is not None:
                if isinstance(profile_data['line1'], QgsGeometry):
                    all_points.extend(profile_data['line1'].asPolyline())
                elif isinstance(profile_data['line1'], list):
                    all_points.extend(profile_data['line1'])
            
            if 'line2' in profile_data and profile_data['line2'] is not None:
                if isinstance(profile_data['line2'], QgsGeometry):
                    all_points.extend(profile_data['line2'].asPolyline())
                elif isinstance(profile_data['line2'], list):
                    all_points.extend(profile_data['line2'])
            
            if all_points:
                x_coords = [p.x() for p in all_points]
                y_coords = [p.y() for p in all_points]
                extent = QgsRectangle(
                    min(x_coords), min(y_coords),
                    max(x_coords), max(y_coords)
                )
        
        if extent:
            extent.scale(1.2)  # 20% buffer
            map_item.setExtent(extent)
        else:
            map_item.setExtent(self.iface.mapCanvas().extent())
    
    def set_adaptive_scale(self, scale_bar, profile_data):
        """Set scale bar units based on section length"""
        # Get section length
        length = 0
        if 'profile1' in profile_data:
            length = profile_data['profile1']['distances'][-1]
        
        # Calculate appropriate scale
        if length > 5000:
            scale_bar.setUnitsPerSegment(1000)  # 1km
        elif length > 1000:
            scale_bar.setUnitsPerSegment(250)   # 250m
        elif length > 500:
            scale_bar.setUnitsPerSegment(100)   # 100m
        elif length > 100:
            scale_bar.setUnitsPerSegment(25)    # 25m
        else:
            scale_bar.setUnitsPerSegment(10)    # 10m
    
    def create_section_info_text(self, profile_data):
        """Create formatted info text for section"""
        import numpy as np
        
        info = "SECTION INFORMATION\n" + "=" * 30 + "\n\n"
        
        # DEM info
        info += f"DEM Source: {profile_data.get('dem1_name', 'Unknown')}\n"
        
        # Section type
        if profile_data.get('single_mode'):
            info += "Type: Single Profile\n"
        else:
            info += "Type: Dual Profile (A-A' / B-B')\n"
        
        # Add basic statistics
        if 'profile1' in profile_data:
            profile1 = profile_data['profile1']
            elev1 = profile1['elevations']
            valid_elev1 = elev1[~np.isnan(elev1)]
            
            info += f"\nProfile A-A':\n"
            info += f"  Length: {profile1['distances'][-1]:.1f} m\n"
            if len(valid_elev1) > 0:
                info += f"  Min Elevation: {np.min(valid_elev1):.2f} m\n"
                info += f"  Max Elevation: {np.max(valid_elev1):.2f} m\n"
                info += f"  Mean Elevation: {np.mean(valid_elev1):.2f} m\n"
                info += f"  Elevation Range: {np.max(valid_elev1) - np.min(valid_elev1):.2f} m\n"
        
        if not profile_data.get('single_mode') and 'profile2' in profile_data and profile_data['profile2'] is not None:
            profile2 = profile_data['profile2']
            elev2 = profile2['elevations']
            valid_elev2 = elev2[~np.isnan(elev2)]
            
            info += f"\nProfile B-B':\n"
            info += f"  Length: {profile2['distances'][-1]:.1f} m\n"
            if len(valid_elev2) > 0:
                info += f"  Min Elevation: {np.min(valid_elev2):.2f} m\n"
                info += f"  Max Elevation: {np.max(valid_elev2):.2f} m\n"
                info += f"  Mean Elevation: {np.mean(valid_elev2):.2f} m\n"
                info += f"  Elevation Range: {np.max(valid_elev2) - np.min(valid_elev2):.2f} m\n"
        
        # Add offset info if dual mode
        if not profile_data.get('single_mode'):
            info += f"\nOffset Distance: {profile_data.get('offset', 0)} m\n"
        
        return info
    
    def add_section_statistics(self, profile_data, x, y):
        """Add compact statistics table for a section"""
        import numpy as np
        
        # Create statistics text
        stats_text = "STATISTICS\n" + "-" * 40 + "\n"
        
        single_mode = profile_data.get('single_mode', False)
        
        if single_mode:
            # Single profile stats
            if 'profile1' in profile_data:
                profile1 = profile_data['profile1']
                elev1 = profile1['elevations']
                valid_elev1 = elev1[~np.isnan(elev1)]
                
                if len(valid_elev1) > 0:
                    stats_text += f"Min: {np.min(valid_elev1):.2f} m\n"
                    stats_text += f"Max: {np.max(valid_elev1):.2f} m\n"
                    stats_text += f"Mean: {np.mean(valid_elev1):.2f} m\n"
                    stats_text += f"Std Dev: {np.std(valid_elev1):.2f} m\n"
        else:
            # Dual profile stats
            header_a = "A-A'"
            header_b = "B-B'"
            stats_text += f"{'':10} {header_a:>12} {header_b:>12}\n"
            stats_text += "-" * 40 + "\n"
            
            if 'profile1' in profile_data and 'profile2' in profile_data:
                profile1 = profile_data['profile1']
                profile2 = profile_data.get('profile2')
                
                elev1 = profile1['elevations']
                valid_elev1 = elev1[~np.isnan(elev1)]
                
                if profile2:
                    elev2 = profile2['elevations']
                    valid_elev2 = elev2[~np.isnan(elev2)]
                    
                    if len(valid_elev1) > 0 and len(valid_elev2) > 0:
                        stats_text += f"{'Min (m)':10} {np.min(valid_elev1):12.2f} {np.min(valid_elev2):12.2f}\n"
                        stats_text += f"{'Max (m)':10} {np.max(valid_elev1):12.2f} {np.max(valid_elev2):12.2f}\n"
                        stats_text += f"{'Mean (m)':10} {np.mean(valid_elev1):12.2f} {np.mean(valid_elev2):12.2f}\n"
        
        # Create label
        stats_label = QgsLayoutItemLabel(self.layout)
        stats_label.setText(stats_text)
        stats_label.setFont(QFont('Courier', 8))
        stats_label.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
        stats_label.attemptResize(QgsLayoutSize(180, 60, QgsUnitTypes.LayoutMillimeters))
        stats_label.setFrameEnabled(True)
        stats_label.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
        stats_label.setMarginX(3)
        stats_label.setMarginY(3)
        self.layout.addLayoutItem(stats_label)
    
    def add_ai_report_page(self, ai_report_text):
        """Add AI report as final page"""
        # Add new page
        page = QgsLayoutItemPage(self.layout)
        page.setPageSize('A3', QgsLayoutItemPage.Landscape)
        self.layout.pageCollection().addPage(page)
        
        page_num = self.layout.pageCollection().pageCount() - 1
        y_offset = page_num * 297
        
        # Add page border
        border = QgsLayoutItemShape(self.layout)
        border.setShapeType(QgsLayoutItemShape.Rectangle)
        border.attemptMove(QgsLayoutPoint(10, 10 + y_offset, QgsUnitTypes.LayoutMillimeters))
        border.attemptResize(QgsLayoutSize(400, 277, QgsUnitTypes.LayoutMillimeters))
        border.setFrameEnabled(True)
        border.setFrameStrokeWidth(QgsLayoutMeasurement(1, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(border)
        
        # Title
        title = QgsLayoutItemLabel(self.layout)
        title.setText("AI ANALYSIS REPORT")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.attemptMove(QgsLayoutPoint(20, 20 + y_offset, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(380, 15, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(title)
        
        # Report content
        report_label = QgsLayoutItemLabel(self.layout)
        report_label.setText(ai_report_text)
        report_label.setFont(QFont('Arial', 10))
        report_label.attemptMove(QgsLayoutPoint(20, 40 + y_offset, QgsUnitTypes.LayoutMillimeters))
        report_label.attemptResize(QgsLayoutSize(380, 240, QgsUnitTypes.LayoutMillimeters))
        report_label.setFrameEnabled(True)
        report_label.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
        report_label.setMarginX(10)
        report_label.setMarginY(10)
        self.layout.addLayoutItem(report_label)
    
    def create_overview_page(self, profile_data, plot_image_path, view_3d_image_path):
        """Create the first overview page"""
        # Check if this is multi-section data
        if profile_data.get('multi_section'):
            # Use multi-section layout
            from .multi_section_layout import MultiSectionLayoutGenerator
            
            # Add border
            self.add_grid_references()
            
            # Add multi-section content
            MultiSectionLayoutGenerator.add_multi_section_to_layout(
                self.layout, profile_data, start_y=50
            )
            
            # Add scale bar and north arrow
            self.add_scale_bar()
            self.add_north_arrow()
            
        else:
            # FIRST: Add border rectangle (so it's under everything)
            self.add_grid_references()
            
            # Add title
            self.add_title(profile_data)
            
            # Add main map showing section lines and store reference
            self.map1 = self.add_main_map(profile_data)
            
            # Add profile plots
            if plot_image_path:
                self.add_profile_plots(plot_image_path)
            
            # Add 3D view
            if view_3d_image_path:
                self.add_3d_view(view_3d_image_path)
            
            # Add statistics table
            self.add_statistics_table(profile_data)
            
            # Add scale bar linked to map1
            self.add_scale_bar()
            
            # Add north arrow
            self.add_north_arrow()
            
            # Add legend on the right
            self.add_legend()
            
            # Add metadata
            self.add_metadata(profile_data)
    
    def add_section_page(self, section_data, section_number, page_number):
        """Add a page for an individual section"""
        # Calculate Y offset for this page
        page_y_offset = (page_number - 1) * 297  # A3 height in mm
        
        # Add border
        border = QgsLayoutItemShape(self.layout)
        border.setShapeType(QgsLayoutItemShape.Rectangle)
        border.attemptMove(QgsLayoutPoint(10, 40 + page_y_offset, QgsUnitTypes.LayoutMillimeters))
        border.attemptResize(QgsLayoutSize(400, 250, QgsUnitTypes.LayoutMillimeters))
        border.setFrameEnabled(True)
        border.setFrameStrokeWidth(QgsLayoutMeasurement(1, QgsUnitTypes.LayoutMillimeters))
        border.setZValue(-1)
        self.layout.addLayoutItem(border)
        
        # Add section title
        title = QgsLayoutItemLabel(self.layout)
        title.setText(f"SECTION {section_number} ANALYSIS")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.attemptMove(QgsLayoutPoint(20, 50 + page_y_offset, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(380, 15, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(title)
        
        # Add section plots if available
        if section_data.get('plot_image'):
            picture = QgsLayoutItemPicture(self.layout)
            picture.setPicturePath(section_data['plot_image'])
            picture.attemptMove(QgsLayoutPoint(20, 70 + page_y_offset, QgsUnitTypes.LayoutMillimeters))
            picture.attemptResize(QgsLayoutSize(380, 200, QgsUnitTypes.LayoutMillimeters))
            picture.setFrameEnabled(True)
            picture.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
            self.layout.addLayoutItem(picture)
        
        # Add section info
        info_text = f"""Section: A{section_number}-A'{section_number} / B{section_number}-B'{section_number}
DEM: {section_data['profile_data'].get('dem1_name', 'Unknown')}
Samples: {len(section_data['profile_data']['profile1']['distances'])}
Offset: {section_data['profile_data'].get('offset', 0)} m"""
        
        info = QgsLayoutItemLabel(self.layout)
        info.setText(info_text)
        info.setFont(QFont('Arial', 10))
        info.attemptMove(QgsLayoutPoint(20, 275 + page_y_offset, QgsUnitTypes.LayoutMillimeters))
        info.attemptResize(QgsLayoutSize(100, 20, QgsUnitTypes.LayoutMillimeters))
        self.layout.addLayoutItem(info)