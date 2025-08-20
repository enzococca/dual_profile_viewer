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
    QgsMapRendererJob, QgsLayoutMeasurement, QgsLayoutTable
)
import tempfile
import os

class LayoutGenerator:
    """Generate professional layouts for profile analysis"""
    
    def __init__(self, iface):
        self.iface = iface
        self.layout = None
        
    def create_profile_layout(self, profile_data, plot_image_path=None, view_3d_image_path=None, all_sections=None):
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
        
        # Determine number of pages needed
        sections_to_show = all_sections if all_sections else [{'profile_data': profile_data, 'plot_image': plot_image_path}]
        num_sections = len(sections_to_show)
        
        # First page - main overview
        page = self.layout.pageCollection().page(0)
        page.setPageSize('A3', QgsLayoutItemPage.Landscape)
        
        # Create first page with overview
        self.create_overview_page(profile_data, plot_image_path, view_3d_image_path)
        
        # Add additional pages for all sections if provided
        if all_sections and len(all_sections) > 1:
            for i, section in enumerate(all_sections):
                # Add new page
                new_page = QgsLayoutItemPage(self.layout)
                new_page.setPageSize('A3', QgsLayoutItemPage.Landscape)
                self.layout.pageCollection().addPage(new_page)
                
                # Add content for this section
                self.add_section_page(section, i + 1, page_number=i + 2)
        
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
        if 'line1' in profile_data and 'line2' in profile_data:
            # Calculate extent from lines
            all_points = profile_data['line1'] + profile_data['line2']
            x_coords = [p.x() for p in all_points]
            y_coords = [p.y() for p in all_points]
            
            extent = QgsRectangle(
                min(x_coords), min(y_coords),
                max(x_coords), max(y_coords)
            )
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
        profile2 = profile_data['profile2']
        
        # Create table as formatted text
        table_text = "STATISTICAL SUMMARY\n\n"
        table_text += "-" * 80 + "\n"
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
            profile2_dem2 = profile_data['profile2_dem2']
            
            min1_2 = np.nanmin(profile1_dem2['elevations'])
            min2_2 = np.nanmin(profile2_dem2['elevations'])
            table_text += f"{'Min Elevation (m)':<25} {min1_2:>15.2f} {min2_2:>15.2f} {(min1_2-min2_2):>15.2f}\n"
            
            max1_2 = np.nanmax(profile1_dem2['elevations'])
            max2_2 = np.nanmax(profile2_dem2['elevations'])
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
    
    def create_overview_page(self, profile_data, plot_image_path, view_3d_image_path):
        """Create the first overview page"""
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