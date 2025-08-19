import subprocess
import sys
import os
import threading
import importlib
import platform
from typing import List, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from qgis.core import QgsMessageLog, Qgis
from qgis.utils import iface


class ModuleInstallerThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, modules: List[str], parent=None):
        super().__init__(parent)
        self.modules = modules
        self.success = True
        self.error_message = ""
        
    def run(self):
        for module in self.modules:
            try:
                self.progress.emit(f"Installing {module}...")
                
                # Get the correct Python executable path
                python_exe = sys.executable
                
                # On macOS, if we're running from QGIS.app, we need to use the correct Python
                if platform.system() == 'Darwin' and 'QGIS' in python_exe:
                    # Try to find the actual Python executable inside QGIS
                    import shutil
                    possible_pythons = [
                        python_exe,
                        shutil.which('python3'),
                        shutil.which('python'),
                        '/usr/bin/python3',
                        '/usr/local/bin/python3'
                    ]
                    
                    # Find the first working Python
                    for py_path in possible_pythons:
                        if py_path and os.path.exists(py_path):
                            python_exe = py_path
                            break
                
                # Build the pip command
                cmd = [python_exe, "-m", "pip", "install", "--user", module]
                
                # Log the command for debugging
                QgsMessageLog.logMessage(f"Running command: {' '.join(cmd)}", "DualProfileViewer", Qgis.Info)
                
                # Use subprocess to install the module
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=os.environ.copy()
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    self.success = False
                    self.error_message = f"Failed to install {module}: {stderr}"
                    self.progress.emit(f"Error installing {module}: {stderr}")
                    break
                else:
                    self.progress.emit(f"Successfully installed {module}")
                    # Try to import the module immediately
                    try:
                        importlib.import_module(module.replace('-', '_'))
                    except:
                        pass
                    
            except Exception as e:
                self.success = False
                self.error_message = f"Exception installing {module}: {str(e)}"
                self.progress.emit(f"Exception during installation of {module}")
                break
                
        self.finished.emit(self.success, self.error_message)


class ModuleInstaller:
    def __init__(self):
        # Only include essential modules that are likely to install successfully
        # Note: matplotlib and numpy are already included in QGIS
        self.required_modules = {
            'scipy': 'scipy',
            'sklearn': 'scikit-learn',
            'PIL': 'Pillow',
            'shapely': 'shapely',
            'tqdm': 'tqdm'
        }
        
        # Optional modules that might fail
        self.optional_modules = {
            'mayavi': 'mayavi',
            'skimage': 'scikit-image',
            'stratigraph': 'stratigraph'
        }
        
    def check_modules(self) -> List[str]:
        missing_modules = []
        
        for import_name, pip_name in self.required_modules.items():
            try:
                importlib.import_module(import_name)
                QgsMessageLog.logMessage(f"Module {import_name} is available", "DualProfileViewer", Qgis.Info)
            except ImportError:
                missing_modules.append(pip_name)
                QgsMessageLog.logMessage(f"Module {import_name} is missing", "DualProfileViewer", Qgis.Warning)
                
        return missing_modules
        
    def install_missing_modules(self, callback: Optional[Callable] = None, 
                             progress_callback: Optional[Callable] = None,
                             parent: Optional[QObject] = None) -> bool:
        missing = self.check_modules()
        
        if not missing:
            QgsMessageLog.logMessage("All required modules are installed", "DualProfileViewer", Qgis.Info)
            if callback:
                callback(True, "All modules already installed")
            return True
            
        QgsMessageLog.logMessage(f"Missing modules: {', '.join(missing)}", "DualProfileViewer", Qgis.Warning)
        
        # Create and start installation thread
        self.installer_thread = ModuleInstallerThread(missing, parent)
        
        if progress_callback:
            self.installer_thread.progress.connect(progress_callback)
            
        if callback:
            self.installer_thread.finished.connect(callback)
            
        self.installer_thread.start()
        
        return False  # Installation in progress
        
    def ensure_modules_available(self) -> bool:
        missing = self.check_modules()
        return len(missing) == 0