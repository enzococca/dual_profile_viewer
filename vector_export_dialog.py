# -*- coding: utf-8 -*-
"""
Vector Export Dialog - Options for exporting profiles as vectors
"""

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt

class VectorExportDialog(QtWidgets.QDialog):
    """Dialog for vector export options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Profile as Vector")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the interface"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Export type
        group_type = QtWidgets.QGroupBox("Export Type")
        type_layout = QtWidgets.QVBoxLayout()
        
        self.radio_polyline = QtWidgets.QRadioButton("Polyline (profile curve)")
        self.radio_polyline.setChecked(True)
        type_layout.addWidget(self.radio_polyline)
        
        self.radio_polygon = QtWidgets.QRadioButton("Polygon (filled area)")
        type_layout.addWidget(self.radio_polygon)
        
        self.radio_3d = QtWidgets.QRadioButton("3D Polyline (with real elevations)")
        type_layout.addWidget(self.radio_3d)
        
        group_type.setLayout(type_layout)
        layout.addWidget(group_type)
        
        # Scale options
        group_scale = QtWidgets.QGroupBox("Scale Options")
        scale_layout = QtWidgets.QFormLayout()
        
        # Overall scale
        self.spin_scale = QtWidgets.QDoubleSpinBox()
        self.spin_scale.setMinimum(0.1)
        self.spin_scale.setMaximum(100.0)
        self.spin_scale.setValue(1.0)
        self.spin_scale.setSingleStep(0.1)
        self.spin_scale.setDecimals(2)
        self.spin_scale.setSuffix("x")
        scale_layout.addRow("Overall Scale:", self.spin_scale)
        
        # Vertical exaggeration
        self.spin_vertical = QtWidgets.QDoubleSpinBox()
        self.spin_vertical.setMinimum(0.1)
        self.spin_vertical.setMaximum(100.0)
        self.spin_vertical.setValue(1.0)
        self.spin_vertical.setSingleStep(0.5)
        self.spin_vertical.setDecimals(1)
        self.spin_vertical.setSuffix("x")
        scale_layout.addRow("Vertical Exaggeration:", self.spin_vertical)
        
        # Baseline offset
        self.spin_baseline = QtWidgets.QDoubleSpinBox()
        self.spin_baseline.setMinimum(0.0)
        self.spin_baseline.setMaximum(1000.0)
        self.spin_baseline.setValue(0.0)
        self.spin_baseline.setSingleStep(1.0)
        self.spin_baseline.setDecimals(1)
        self.spin_baseline.setSuffix(" m")
        scale_layout.addRow("Baseline Offset:", self.spin_baseline)
        
        group_scale.setLayout(scale_layout)
        layout.addWidget(group_scale)
        
        # Options
        group_options = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout()
        
        self.check_add_to_map = QtWidgets.QCheckBox("Add to map after export")
        self.check_add_to_map.setChecked(True)
        options_layout.addWidget(self.check_add_to_map)
        
        self.check_style = QtWidgets.QCheckBox("Apply default styling")
        self.check_style.setChecked(True)
        options_layout.addWidget(self.check_style)
        
        group_options.setLayout(options_layout)
        layout.addWidget(group_options)
        
        # Info label
        info_label = QtWidgets.QLabel(
            "<b>Note:</b> The profile will be georeferenced and scaled "
            "perpendicular to the original profile line, maintaining "
            "the elevation shape as a geographic feature."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; }")
        layout.addWidget(info_label)
        
        # Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_options(self):
        """Get selected options"""
        export_type = 'polyline'
        if self.radio_polygon.isChecked():
            export_type = 'polygon'
        elif self.radio_3d.isChecked():
            export_type = '3d'
        
        return {
            'type': export_type,
            'scale': self.spin_scale.value(),
            'vertical_exag': self.spin_vertical.value(),
            'baseline_offset': self.spin_baseline.value(),
            'add_to_map': self.check_add_to_map.isChecked(),
            'apply_style': self.check_style.isChecked()
        }
