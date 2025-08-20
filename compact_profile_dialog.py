# -*- coding: utf-8 -*-
"""
Compact Profile Dialog with tabs and integrated web view
"""

from qgis.PyQt import QtWidgets, QtCore
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtWidgets import (QTabWidget, QVBoxLayout, QHBoxLayout, 
                                QWidget, QSplitter, QGroupBox, QToolButton,
                                QSizePolicy)

# Try to import QWebEngineView
try:
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    try:
        from qgis.PyQt.QtWebKitWidgets import QWebView as QWebEngineView
        WEBENGINE_AVAILABLE = True
    except ImportError:
        WEBENGINE_AVAILABLE = False

from .multi_dem_widget import MultiDEMWidget
import tempfile
import os

# Import plotly
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class CompactProfileDialog(QtWidgets.QWidget):
    """Compact tabbed interface for profile viewer"""
    
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.map_tool = None
        self.profile_data = None
        self.profile_data_list = []
        self.web_view = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create compact tabbed interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Tab 1: Profile Settings
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Tab 2: DEM Selection
        self.dem_tab = self.create_dem_tab()
        self.tab_widget.addTab(self.dem_tab, "DEMs")
        
        # Tab 3: Export Options
        self.export_tab = self.create_export_tab()
        self.tab_widget.addTab(self.export_tab, "Export")
        
        # Tab 4: 3D View
        self.view3d_tab = self.create_3d_tab()
        self.tab_widget.addTab(self.view3d_tab, "3D View")
        
        # Create splitter for tab widget and plot area
        splitter = QSplitter(Qt.Vertical)
        
        # Top part: compact toolbar and tabs
        top_widget = QWidget()
        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Compact toolbar
        toolbar = self.create_compact_toolbar()
        top_layout.addWidget(toolbar)
        top_layout.addWidget(self.tab_widget)
        
        top_widget.setLayout(top_layout)
        splitter.addWidget(top_widget)
        
        # Bottom part: Web view for plots
        if WEBENGINE_AVAILABLE and PLOTLY_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setMinimumHeight(300)
            splitter.addWidget(self.web_view)
            
            # Show initial message
            self.show_welcome_plot()
        else:
            # Fallback to text widget
            self.plot_info = QtWidgets.QTextEdit()
            self.plot_info.setReadOnly(True)
            self.plot_info.setMinimumHeight(300)
            self.plot_info.setHtml("""
                <h3>Plotly Visualization</h3>
                <p>To enable integrated plots, install:</p>
                <pre>pip install plotly</pre>
                <p>Current status:</p>
                <ul>
                <li>Plotly: {}</li>
                <li>WebEngine: {}</li>
                </ul>
            """.format(
                "✓ Installed" if PLOTLY_AVAILABLE else "✗ Not installed",
                "✓ Available" if WEBENGINE_AVAILABLE else "✗ Not available"
            ))
            splitter.addWidget(self.plot_info)
        
        # Set splitter sizes (30% top, 70% bottom)
        splitter.setSizes([200, 400])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_compact_toolbar(self):
        """Create compact toolbar with essential actions"""
        toolbar = QtWidgets.QToolBar()
        toolbar.setIconSize(QtCore.QSize(24, 24))
        
        # Draw action
        self.draw_action = toolbar.addAction("📏 Draw")
        self.draw_action.setToolTip("Draw profile sections")
        self.draw_action.triggered.connect(self.start_drawing)
        
        toolbar.addSeparator()
        
        # Create profiles action
        self.create_action = toolbar.addAction("📊 Create")
        self.create_action.setToolTip("Create elevation profiles")
        self.create_action.triggered.connect(self.create_profiles)
        self.create_action.setEnabled(False)
        
        # Clear action
        self.clear_action = toolbar.addAction("🗑️ Clear")
        self.clear_action.setToolTip("Clear current profiles")
        self.clear_action.triggered.connect(self.clear_profiles)
        
        toolbar.addSeparator()
        
        # Quick export
        self.export_action = toolbar.addAction("💾 Export")
        self.export_action.setToolTip("Quick export profiles")
        self.export_action.triggered.connect(self.quick_export)
        self.export_action.setEnabled(False)
        
        # 3D view
        self.view3d_action = toolbar.addAction("🎲 3D")
        self.view3d_action.setToolTip("Open 3D viewer")
        self.view3d_action.triggered.connect(self.open_3d_viewer)
        self.view3d_action.setEnabled(False)
        
        toolbar.addSeparator()
        
        # Help
        self.help_action = toolbar.addAction("❓ Help")
        self.help_action.setToolTip("Show help")
        self.help_action.triggered.connect(self.show_help)
        
        return toolbar
        
    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Primary DEM selection
        dem_group = QGroupBox("Primary DEM")
        dem_layout = QVBoxLayout()
        
        self.combo_dem = QtWidgets.QComboBox()
        self.load_raster_layers(self.combo_dem)
        dem_layout.addWidget(self.combo_dem)
        
        dem_group.setLayout(dem_layout)
        layout.addWidget(dem_group)
        
        # Profile parameters
        params_group = QGroupBox("Profile Parameters")
        params_layout = QtWidgets.QFormLayout()
        
        # Offset
        self.spin_distance = QtWidgets.QDoubleSpinBox()
        self.spin_distance.setMinimum(0.05)
        self.spin_distance.setMaximum(500.0)
        self.spin_distance.setValue(1.0)
        self.spin_distance.setSingleStep(0.05)
        self.spin_distance.setDecimals(2)
        self.spin_distance.setSuffix(" m")
        params_layout.addRow("Offset:", self.spin_distance)
        
        # Samples
        self.spin_samples = QtWidgets.QSpinBox()
        self.spin_samples.setMinimum(10)
        self.spin_samples.setMaximum(2000)
        self.spin_samples.setValue(200)
        params_layout.addRow("Samples:", self.spin_samples)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_dem_tab(self):
        """Create DEM selection tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Multi-DEM comparison
        self.check_multi_dem = QtWidgets.QCheckBox("Compare Multiple DEMs")
        self.check_multi_dem.toggled.connect(self.on_multi_dem_toggled)
        layout.addWidget(self.check_multi_dem)
        
        # Multi-DEM widget
        self.multi_dem_widget = MultiDEMWidget()
        self.multi_dem_widget.setVisible(False)
        layout.addWidget(self.multi_dem_widget)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_export_tab(self):
        """Create export options tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Export formats
        formats_group = QGroupBox("Export Formats")
        formats_layout = QVBoxLayout()
        
        self.export_csv_btn = QtWidgets.QPushButton("📄 Export as CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        formats_layout.addWidget(self.export_csv_btn)
        
        self.export_vector_btn = QtWidgets.QPushButton("📐 Export as Vector")
        self.export_vector_btn.clicked.connect(self.export_vector)
        formats_layout.addWidget(self.export_vector_btn)
        
        self.export_png_btn = QtWidgets.QPushButton("🖼️ Export as Image")
        self.export_png_btn.clicked.connect(self.export_png)
        formats_layout.addWidget(self.export_png_btn)
        
        formats_group.setLayout(formats_layout)
        layout.addWidget(formats_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_3d_tab(self):
        """Create 3D view options tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 3D options
        options_group = QGroupBox("3D Visualization Options")
        options_layout = QVBoxLayout()
        
        self.use_pyvista_check = QtWidgets.QCheckBox("Use PyVista (if available)")
        self.use_pyvista_check.setChecked(True)
        options_layout.addWidget(self.use_pyvista_check)
        
        self.use_plotly_check = QtWidgets.QCheckBox("Use Plotly 3D")
        options_layout.addWidget(self.use_plotly_check)
        
        self.use_matplotlib_check = QtWidgets.QCheckBox("Use Matplotlib 3D")
        options_layout.addWidget(self.use_matplotlib_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 3D viewer button
        self.open_3d_btn = QtWidgets.QPushButton("🎲 Open 3D Viewer")
        self.open_3d_btn.clicked.connect(self.open_3d_viewer)
        layout.addWidget(self.open_3d_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def show_welcome_plot(self):
        """Show welcome message in web view"""
        if not self.web_view or not PLOTLY_AVAILABLE:
            return
            
        # Create welcome plot
        fig = go.Figure()
        
        # Add text annotation
        fig.add_annotation(
            text="<b>Dual Profile Viewer</b><br><br>Draw sections on the map to create elevation profiles",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16),
            align="center"
        )
        
        # Update layout
        fig.update_layout(
            title="Welcome",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Generate HTML
        html = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')
        full_html = f"""
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 10px; }}
                .plotly-graph-div {{ width: 100% !important; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Load in web view
        self.web_view.setHtml(full_html)
        
    def update_plot(self):
        """Update the integrated plot view"""
        if not self.web_view or not PLOTLY_AVAILABLE or not self.profile_data:
            return
            
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Profile A-A\'', 'Profile B-B\'')
        )
        
        # Add profile 1
        profile1 = self.profile_data.get('profile1', {})
        if 'distances' in profile1 and 'elevations' in profile1:
            fig.add_trace(
                go.Scatter(
                    x=profile1['distances'],
                    y=profile1['elevations'],
                    mode='lines',
                    name='A-A\'',
                    line=dict(color='red', width=2)
                ),
                row=1, col=1
            )
        
        # Add profile 2
        profile2 = self.profile_data.get('profile2', {})
        if 'distances' in profile2 and 'elevations' in profile2:
            fig.add_trace(
                go.Scatter(
                    x=profile2['distances'],
                    y=profile2['elevations'],
                    mode='lines',
                    name='B-B\'',
                    line=dict(color='blue', width=2)
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
        fig.update_yaxes(title_text="Elevation (m)", row=1, col=1)
        fig.update_yaxes(title_text="Elevation (m)", row=2, col=1)
        
        fig.update_layout(
            height=500,
            showlegend=True,
            title_text="Elevation Profiles",
            hovermode='x unified'
        )
        
        # Generate HTML
        html = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')
        full_html = f"""
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 5px; }}
                .plotly-graph-div {{ width: 100% !important; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(full_html)
            temp_path = f.name
            
        # Load in web view
        self.web_view.load(QUrl.fromLocalFile(temp_path))
        
    def load_raster_layers(self, combo):
        """Load available raster layers into combo box"""
        from qgis.core import QgsProject, QgsRasterLayer
        
        combo.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsRasterLayer) and layer.isValid():
                combo.addItem(layer.name(), layer.id())
                
    def on_multi_dem_toggled(self, checked):
        """Toggle multi-DEM widget visibility"""
        self.multi_dem_widget.setVisible(checked)
        
    # Placeholder methods for actions
    def start_drawing(self):
        pass
        
    def create_profiles(self):
        pass
        
    def clear_profiles(self):
        pass
        
    def quick_export(self):
        pass
        
    def open_3d_viewer(self):
        pass
        
    def show_help(self):
        pass
        
    def export_csv(self):
        pass
        
    def export_vector(self):
        pass
        
    def export_png(self):
        pass