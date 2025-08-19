import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QSpinBox, QCheckBox, QPushButton,
    QDoubleSpinBox, QComboBox, QMessageBox,
    QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from qgis.core import QgsMessageLog, Qgis

from .module_installer import ModuleInstaller
from .manual_install_dialog import ManualInstallDialog
from .stratigraph_integration import StratigraphIntegration, STRATIGRAPH_AVAILABLE, MAYAVI_AVAILABLE


class Stratigraph3DDialog(QDialog):
    visualization_requested = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Stratigraphic Visualization")
        self.setMinimumWidth(400)
        self.module_installer = ModuleInstaller()
        self.stratigraph = StratigraphIntegration()
        
        self.init_ui()
        self.check_modules()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Module status group
        status_group = QGroupBox("Module Status")
        status_layout = QVBoxLayout()
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        status_layout.addWidget(self.status_text)
        
        button_layout = QHBoxLayout()
        
        self.install_button = QPushButton("Auto Install")
        self.install_button.clicked.connect(self.install_modules)
        button_layout.addWidget(self.install_button)
        
        self.manual_install_button = QPushButton("Manual Install Instructions")
        self.manual_install_button.clicked.connect(self.show_manual_install)
        button_layout.addWidget(self.manual_install_button)
        
        status_layout.addLayout(button_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Visualization settings
        viz_group = QGroupBox("Visualization Settings")
        viz_layout = QVBoxLayout()
        
        # Layer settings
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel("Number of layers:"))
        self.layer_count_spin = QSpinBox()
        self.layer_count_spin.setMinimum(2)
        self.layer_count_spin.setMaximum(50)
        self.layer_count_spin.setValue(10)
        layer_layout.addWidget(self.layer_count_spin)
        viz_layout.addLayout(layer_layout)
        
        # Cross-section settings
        cross_layout = QHBoxLayout()
        cross_layout.addWidget(QLabel("Cross-section width (m):"))
        self.cross_width_spin = QDoubleSpinBox()
        self.cross_width_spin.setMinimum(10)
        self.cross_width_spin.setMaximum(1000)
        self.cross_width_spin.setValue(100)
        self.cross_width_spin.setSingleStep(10)
        cross_layout.addWidget(self.cross_width_spin)
        viz_layout.addLayout(cross_layout)
        
        # Display options
        self.show_layers_check = QCheckBox("Show layer boundaries")
        self.show_layers_check.setChecked(True)
        viz_layout.addWidget(self.show_layers_check)
        
        self.exploded_view_check = QCheckBox("Exploded view")
        viz_layout.addWidget(self.exploded_view_check)
        
        self.show_grid_check = QCheckBox("Show grid")
        self.show_grid_check.setChecked(True)
        viz_layout.addWidget(self.show_grid_check)
        
        # Colormap selection
        colormap_layout = QHBoxLayout()
        colormap_layout.addWidget(QLabel("Colormap:"))
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(['terrain', 'viridis', 'plasma', 'coolwarm', 'seismic'])
        colormap_layout.addWidget(self.colormap_combo)
        viz_layout.addLayout(colormap_layout)
        
        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)
        
        # Additional analysis options
        analysis_group = QGroupBox("Stratigraphic Analysis")
        analysis_layout = QVBoxLayout()
        
        self.wheeler_diagram_check = QCheckBox("Generate Wheeler diagram")
        analysis_layout.addWidget(self.wheeler_diagram_check)
        
        self.barrell_plot_check = QCheckBox("Generate Barrell plot")
        analysis_layout.addWidget(self.barrell_plot_check)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.visualize_button = QPushButton("Create 3D Visualization")
        self.visualize_button.clicked.connect(self.create_visualization)
        button_layout.addWidget(self.visualize_button)
        
        self.cancel_button = QPushButton("Close")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def check_modules(self):
        status_text = []
        
        if STRATIGRAPH_AVAILABLE:
            status_text.append("✓ Stratigraph module is installed")
        else:
            status_text.append("✗ Stratigraph module is NOT installed")
            
        # Check visualization libraries
        try:
            import plotly
            status_text.append("✓ Plotly is installed (interactive 3D with measurements)")
        except ImportError:
            status_text.append("✗ Plotly not installed (using matplotlib fallback)")
            
        status_text.append("✓ Matplotlib 3D visualization (always available)")
            
        missing = self.module_installer.check_modules()
        
        # Always enable manual install button
        self.manual_install_button.setEnabled(True)
        
        # We can use matplotlib 3D viewer as fallback, so always enable visualization
        self.visualize_button.setEnabled(True)
        
        if missing:
            status_text.append(f"\nMissing modules: {', '.join(missing)}")
            status_text.append("\nNote: Basic 3D visualization will work with matplotlib only")
            self.install_button.setEnabled(True)
        else:
            status_text.append("\nAll required modules are installed!")
            self.install_button.setEnabled(False)
            
        self.status_text.setPlainText('\n'.join(status_text))
        
    def install_modules(self):
        self.install_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        def on_progress(message):
            self.status_text.append(message)
            QgsMessageLog.logMessage(message, "DualProfileViewer", Qgis.Info)
            
        def on_finished(success, message):
            self.progress_bar.setVisible(False)
            self.progress_bar.setRange(0, 100)
            
            if success:
                QMessageBox.information(self, "Installation Complete", 
                                      "All modules have been installed successfully!\n"
                                      "Please restart QGIS to use the new modules.")
                self.check_modules()
            else:
                QMessageBox.critical(self, "Installation Failed", 
                                   f"Failed to install modules:\n{message}")
                self.install_button.setEnabled(True)
                
        self.module_installer.install_missing_modules(
            callback=on_finished,
            progress_callback=on_progress,
            parent=self
        )
        
    def create_visualization(self):
        # Always proceed with visualization using matplotlib
        settings = {
            'layer_count': self.layer_count_spin.value(),
            'cross_width': self.cross_width_spin.value(),
            'show_layers': self.show_layers_check.isChecked(),
            'exploded_view': self.exploded_view_check.isChecked(),
            'show_grid': self.show_grid_check.isChecked(),
            'colormap': self.colormap_combo.currentText(),
            'wheeler_diagram': self.wheeler_diagram_check.isChecked(),
            'barrell_plot': self.barrell_plot_check.isChecked()
        }
        
        self.visualization_requested.emit(settings)
        self.accept()
        
    def show_manual_install(self):
        missing = self.module_installer.check_modules()
        if missing:
            dialog = ManualInstallDialog(missing, self)
            dialog.exec_()