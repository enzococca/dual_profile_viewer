from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton,
    QHBoxLayout, QLabel, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor
import sys
import platform


class ManualInstallDialog(QDialog):
    def __init__(self, missing_modules, parent=None):
        super().__init__(parent)
        self.missing_modules = missing_modules
        self.setWindowTitle("Manual Module Installation")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("Automatic installation failed. Please install the modules manually:")
        layout.addWidget(info_label)
        
        # Installation instructions
        instructions_group = QGroupBox("Installation Instructions")
        instructions_layout = QVBoxLayout()
        
        self.instructions_text = QTextEdit()
        self.instructions_text.setReadOnly(True)
        
        # Generate platform-specific instructions
        instructions = self.generate_instructions()
        self.instructions_text.setHtml(instructions)
        
        instructions_layout.addWidget(self.instructions_text)
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        
        # Python console command
        console_group = QGroupBox("QGIS Python Console Command")
        console_layout = QVBoxLayout()
        
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setMaximumHeight(80)
        self.console_text.setFont(QFont("Courier", 10))
        
        # Generate pip command
        pip_command = self.generate_pip_command()
        self.console_text.setPlainText(pip_command)
        
        console_layout.addWidget(self.console_text)
        
        copy_button = QPushButton("Copy Command")
        copy_button.clicked.connect(self.copy_command)
        console_layout.addWidget(copy_button)
        
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
    def generate_instructions(self):
        system = platform.system()
        
        base_html = """
        <html>
        <body>
        <h3>Method 1: Using QGIS Python Console</h3>
        <ol>
        <li>Open QGIS Python Console (Plugins → Python Console)</li>
        <li>Copy and paste the command from the box below</li>
        <li>Press Enter to execute</li>
        <li>Restart QGIS after installation</li>
        </ol>
        """
        
        if system == "Darwin":  # macOS
            platform_specific = """
            <h3>Method 2: Using Terminal</h3>
            <ol>
            <li>Open Terminal.app</li>
            <li>Find QGIS Python path: <code>/Applications/QGIS.app/Contents/MacOS/bin/python3</code></li>
            <li>Run: <code>/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install --user {}</code></li>
            </ol>
            
            <h3>Method 3: Using Homebrew Python</h3>
            <ol>
            <li>If you have Homebrew: <code>brew install python</code></li>
            <li>Then: <code>python3 -m pip install {}</code></li>
            </ol>
            """.format(' '.join(self.missing_modules), ' '.join(self.missing_modules))
            
        elif system == "Windows":
            platform_specific = """
            <h3>Method 2: Using OSGeo4W Shell</h3>
            <ol>
            <li>Open OSGeo4W Shell from Start Menu</li>
            <li>Run: <code>python -m pip install {}</code></li>
            </ol>
            
            <h3>Method 3: Using Command Prompt</h3>
            <ol>
            <li>Open Command Prompt as Administrator</li>
            <li>Navigate to QGIS Python: <code>cd "C:\\Program Files\\QGIS 3.xx\\apps\\Python39"</code></li>
            <li>Run: <code>python -m pip install {}</code></li>
            </ol>
            """.format(' '.join(self.missing_modules), ' '.join(self.missing_modules))
            
        else:  # Linux
            platform_specific = """
            <h3>Method 2: Using System Terminal</h3>
            <ol>
            <li>Open Terminal</li>
            <li>Run: <code>python3 -m pip install --user {}</code></li>
            </ol>
            
            <h3>Method 3: Using System Package Manager</h3>
            <p>For Ubuntu/Debian:</p>
            <code>sudo apt-get install python3-matplotlib python3-numpy python3-scipy</code>
            
            <p>For Fedora:</p>
            <code>sudo dnf install python3-matplotlib python3-numpy python3-scipy</code>
            """.format(' '.join(self.missing_modules))
            
        notes = """
        <h3>Important Notes:</h3>
        <ul>
        <li><b>Mayavi</b> requires additional system dependencies (VTK) and may be difficult to install</li>
        <li><b>stratigraph</b> is optional and can be skipped if installation fails</li>
        <li>Core features work with just matplotlib, numpy, and scipy</li>
        </ul>
        
        <h3>Troubleshooting:</h3>
        <ul>
        <li>If pip is not found, try: <code>python -m ensurepip</code></li>
        <li>For permission errors, use: <code>--user</code> flag</li>
        <li>On macOS, you may need Xcode Command Line Tools</li>
        </ul>
        </body>
        </html>
        """
        
        return base_html + platform_specific + notes
        
    def generate_pip_command(self):
        # Generate a pip command that can be run in QGIS Python Console
        modules_str = ' '.join(self.missing_modules)
        
        # Multi-line command for QGIS console
        command = f"""import subprocess, sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', {', '.join([f"'{m}'" for m in self.missing_modules])}])
print('Installation complete! Please restart QGIS.')"""
        
        return command
        
    def copy_command(self):
        # Copy the command to clipboard
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.console_text.toPlainText())