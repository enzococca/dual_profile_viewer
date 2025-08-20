#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test QWebEngineView functionality
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QUrl

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    print("✓ QWebEngineView imported successfully")
    WEBENGINE_AVAILABLE = True
except ImportError as e:
    print(f"✗ Failed to import QWebEngineView: {e}")
    WEBENGINE_AVAILABLE = False

if WEBENGINE_AVAILABLE:
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("WebEngine Test")
    
    # Create central widget
    central = QWidget()
    layout = QVBoxLayout()
    
    # Create web view
    web_view = QWebEngineView()
    
    # Test HTML content
    html = """
    <html>
    <head>
        <style>
            body { 
                font-family: Arial; 
                padding: 20px;
                background-color: #f0f0f0;
            }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>QWebEngineView is working!</h1>
        <p>If you can see this, WebEngine is functioning correctly.</p>
        <div id="plot">Plotly would appear here</div>
    </body>
    </html>
    """
    
    web_view.setHtml(html)
    
    # Add button to test loading
    btn = QPushButton("Load Google")
    btn.clicked.connect(lambda: web_view.load(QUrl("https://www.google.com")))
    
    layout.addWidget(web_view)
    layout.addWidget(btn)
    central.setLayout(layout)
    
    window.setCentralWidget(central)
    window.resize(800, 600)
    window.show()
    
    print("\nWebEngine test window opened. Check if content is displayed.")
    print("If the window is blank, there may be a WebEngine issue.")
    
    sys.exit(app.exec_())
else:
    print("\nWebEngine is not available. Cannot run test.")