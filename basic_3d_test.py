"""
Basic 3D test - minimal code
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTextEdit
from qgis.core import QgsMessageLog, Qgis

class Basic3DTest(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Basic 3D Test")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Text widget to show results
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)
        
        # Test button
        test_btn = QPushButton("Run 3D Test")
        test_btn.clicked.connect(self.run_test)
        layout.addWidget(test_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Auto-run test
        self.run_test()
        
    def log(self, msg):
        self.text.append(msg)
        QgsMessageLog.logMessage(msg, "DualProfileViewer", Qgis.Info)
        
    def run_test(self):
        self.text.clear()
        self.log("Starting 3D test...")
        
        # Step 1: Import matplotlib
        try:
            import matplotlib
            self.log(f"✓ Matplotlib {matplotlib.__version__}")
            
            # Step 2: Set backend
            matplotlib.use('Qt5Agg')
            self.log(f"✓ Backend: {matplotlib.get_backend()}")
            
            # Step 3: Create figure
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            
            fig = Figure(figsize=(6, 4))
            canvas = FigureCanvas(fig)
            self.log("✓ Created figure and canvas")
            
            # Step 4: Add 3D plot
            ax = fig.add_subplot(111, projection='3d')
            
            # Simple data
            import numpy as np
            x = np.array([1, 2, 3, 4, 5])
            y = np.array([1, 2, 3, 4, 5])
            z = np.array([1, 4, 9, 16, 25])
            
            ax.plot(x, y, z, 'ro-')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('Test 3D Plot')
            
            self.log("✓ Created 3D plot")
            
            # Step 5: Add canvas to layout
            self.layout().insertWidget(1, canvas)
            canvas.draw()
            
            self.log("✓ 3D visualization working!")
            
        except Exception as e:
            self.log(f"✗ Error: {str(e)}")
            import traceback
            self.log(traceback.format_exc())

# Function to show test
def show_basic_3d_test():
    from qgis.utils import iface
    dialog = Basic3DTest(iface.mainWindow())
    dialog.exec_()
    
if __name__ == '__main__':
    show_basic_3d_test()