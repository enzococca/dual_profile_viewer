# -*- coding: utf-8 -*-
"""
AI Report Generator (Optional)
Generates analysis reports using AI services
"""

import json
import requests
import numpy as np
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                QTextEdit, QPushButton, QLabel,
                                QComboBox, QGroupBox, QLineEdit,
                                QCheckBox)
from qgis.core import QgsMessageLog, Qgis, QgsSettings

class AIReportGenerator(QDialog):
    """Dialog for AI-powered report generation"""
    
    def __init__(self, profile_data, parent=None):
        super().__init__(parent)
        self.profile_data = profile_data
        self.setWindowTitle("AI Report Generator")
        self.resize(800, 600)
        self.generated_report = None  # Store generated report
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        layout = QVBoxLayout()
        
        # API Settings
        api_group = QGroupBox("AI Service Settings")
        api_layout = QVBoxLayout()
        
        # Service selection
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("AI Service:"))
        self.service_combo = QComboBox()
        self.service_combo.addItems(["OpenAI GPT-4", "Anthropic Claude", "Local LLM"])
        self.service_combo.currentTextChanged.connect(self.on_service_changed)
        service_layout.addWidget(self.service_combo)
        api_layout.addLayout(service_layout)
        
        # API Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        
        # Load saved API key
        settings = QgsSettings()
        saved_key = settings.value("dual_profile_viewer/ai_api_key", "")
        self.api_key_edit.setText(saved_key)
        
        key_layout.addWidget(self.api_key_edit)
        api_layout.addLayout(key_layout)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Report Options
        options_group = QGroupBox("Report Options")
        options_layout = QVBoxLayout()
        
        self.include_stats_cb = QCheckBox("Include Statistical Analysis")
        self.include_stats_cb.setChecked(True)
        options_layout.addWidget(self.include_stats_cb)
        
        self.include_interpretation_cb = QCheckBox("Include Geological Interpretation")
        self.include_interpretation_cb.setChecked(True)
        options_layout.addWidget(self.include_interpretation_cb)
        
        self.include_recommendations_cb = QCheckBox("Include Recommendations")
        self.include_recommendations_cb.setChecked(True)
        options_layout.addWidget(self.include_recommendations_cb)
        
        self.technical_level_combo = QComboBox()
        self.technical_level_combo.addItems(["Basic", "Intermediate", "Advanced"])
        self.technical_level_combo.setCurrentIndex(1)
        tech_layout = QHBoxLayout()
        tech_layout.addWidget(QLabel("Technical Level:"))
        tech_layout.addWidget(self.technical_level_combo)
        tech_layout.addStretch()
        options_layout.addLayout(tech_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Report Preview
        preview_group = QGroupBox("Report Preview")
        preview_layout = QVBoxLayout()
        
        self.report_text = QTextEdit()
        self.report_text.setPlaceholderText("AI-generated report will appear here...")
        preview_layout.addWidget(self.report_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.clicked.connect(self.generate_report)
        button_layout.addWidget(self.generate_btn)
        
        self.export_btn = QPushButton("Export Report")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def on_service_changed(self, service):
        """Handle AI service selection change"""
        if service == "Local LLM":
            self.api_key_edit.setEnabled(False)
            self.api_key_edit.setPlaceholderText("Not required for local LLM")
        else:
            self.api_key_edit.setEnabled(True)
            self.api_key_edit.setPlaceholderText("Enter your API key")
            
    def generate_report(self):
        """Generate AI report"""
        try:
            # Save API key
            settings = QgsSettings()
            settings.setValue("dual_profile_viewer/ai_api_key", self.api_key_edit.text())
            
            # Prepare data for AI
            prompt = self.prepare_prompt()
            
            # Call AI service
            service = self.service_combo.currentText()
            if service == "OpenAI GPT-4":
                report = self.generate_openai_report(prompt)
            elif service == "Anthropic Claude":
                report = self.generate_claude_report(prompt)
            else:
                report = self.generate_local_report(prompt)
            
            # Display report
            self.report_text.setHtml(report)
            self.export_btn.setEnabled(True)
            
            # Store plain text version for layout
            self.generated_report = self.report_text.toPlainText()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            
    def prepare_prompt(self):
        """Prepare prompt for AI"""
        if self.profile_data.get('all_sections'):
            return self.prepare_all_sections_prompt()
        elif self.profile_data.get('multi_section'):
            return self.prepare_multi_section_prompt()
        else:
            return self.prepare_standard_prompt()
            
    def prepare_all_sections_prompt(self):
        """Prepare prompt for all sections analysis"""
        all_sections = self.profile_data.get('all_sections', [])
        
        prompt = f"""Analyze the following geological profile data from {len(all_sections)} separate survey sections:

**Total Sections Analyzed**: {len(all_sections)}
**Primary DEM Source**: {self.profile_data.get('dem1_name', 'Unknown')}

**Individual Section Data**:
"""
        
        # Add data for each section
        for idx, section_data in enumerate(all_sections):
            profile_data = section_data['profile_data']
            section_num = section_data.get('section_number', idx + 1)
            
            prompt += f"\n**Section {section_num}:**"
            prompt += f"\n  - DEM: {profile_data.get('dem1_name', 'Unknown')}"
            prompt += f"\n  - Type: {'Single Profile' if profile_data.get('single_mode') else 'Dual Profile'}"
            
            # Add statistics for profile A
            if 'profile1' in profile_data:
                profile1 = profile_data['profile1']
                elev1 = profile1['elevations']
                valid_elev1 = elev1[~np.isnan(elev1)]
                if len(valid_elev1) > 0:
                    prompt += f"\n  - Profile A-A': Length {profile1['distances'][-1]:.1f}m, "
                    prompt += f"Elev {np.min(valid_elev1):.1f}-{np.max(valid_elev1):.1f}m "
                    prompt += f"(mean {np.mean(valid_elev1):.1f}m)"
            
            # Add statistics for profile B if dual mode
            if not profile_data.get('single_mode') and 'profile2' in profile_data and profile_data['profile2'] is not None:
                profile2 = profile_data['profile2']
                elev2 = profile2['elevations']
                valid_elev2 = elev2[~np.isnan(elev2)]
                if len(valid_elev2) > 0:
                    prompt += f"\n  - Profile B-B': Length {profile2['distances'][-1]:.1f}m, "
                    prompt += f"Elev {np.min(valid_elev2):.1f}-{np.max(valid_elev2):.1f}m "
                    prompt += f"(mean {np.mean(valid_elev2):.1f}m)"
        
        prompt += "\n\nPlease provide:"
        
        if self.include_stats_cb.isChecked():
            prompt += "\n1. Comparative statistical analysis across all sections"
        
        if self.include_interpretation_cb.isChecked():
            prompt += "\n2. Geological/archaeological interpretation of the terrain patterns"
        
        if self.include_recommendations_cb.isChecked():
            prompt += "\n3. Recommendations for further investigation"
        
        prompt += f"\n\nTechnical level: {self.technical_level_combo.currentText()}"
        
        return prompt
            
    def prepare_multi_section_prompt(self):
        """Prepare prompt for multi-section analysis"""
        sections = self.profile_data.get('sections', [])
        
        prompt = f"""Analyze the following geological profile data from a polygon survey with {len(sections)} sections:

**Survey Type**: Polygon Section Analysis
**Number of Sections**: {len(sections)}
**DEM Source**: {self.profile_data.get('dem1_name', 'Unknown')}

**Section Data**:
"""
        
        # Add section statistics
        from .multi_section_handler import MultiSectionHandler
        stats = MultiSectionHandler.calculate_multi_section_statistics(sections)
        
        for key in sorted(stats.keys()):
            if key.startswith('section_'):
                section = stats[key]
                prompt += f"\n{section['name']}:"
                prompt += f"\n  - Length: {section['length']:.1f} m"
                prompt += f"\n  - Elevation Range: {section['min_elevation']:.1f} - {section['max_elevation']:.1f} m"
                prompt += f"\n  - Mean Elevation: {section['mean_elevation']:.1f} m"
        
        # Add overall statistics
        if 'overall' in stats:
            overall = stats['overall']
            prompt += f"\n\n**Overall Statistics**:"
            prompt += f"\n  - Total Perimeter: {overall['total_length']:.1f} m"
            prompt += f"\n  - Elevation Range: {overall['elevation_range']:.1f} m"
        
        prompt += "\n\nPlease provide:"
        
        if self.include_stats_cb.isChecked():
            prompt += "\n1. Statistical analysis of the elevation patterns"
        
        if self.include_interpretation_cb.isChecked():
            prompt += "\n2. Geological/archaeological interpretation of the terrain"
        
        if self.include_recommendations_cb.isChecked():
            prompt += "\n3. Recommendations for further investigation"
        
        prompt += f"\n\nTechnical level: {self.technical_level_combo.currentText()}"
        
        return prompt
        
    def prepare_standard_prompt(self):
        """Prepare prompt for standard dual profile"""
        # Implementation for standard profiles
        prompt = "Analyze the following elevation profile data:\n\n"
        
        # Add profile statistics
        if 'profile1' in self.profile_data:
            profile1 = self.profile_data['profile1']
            prompt += f"Profile A-A':\n"
            prompt += f"  - Length: {profile1['distances'][-1]:.1f} m\n"
            prompt += f"  - Elevation range: {profile1['elevations'].min():.1f} - {profile1['elevations'].max():.1f} m\n"
        
        return prompt
        
    def generate_openai_report(self, prompt):
        """Generate report using OpenAI"""
        api_key = self.api_key_edit.text()
        if not api_key:
            raise ValueError("OpenAI API key required")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a geological and archaeological analysis expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return self.format_report(result['choices'][0]['message']['content'])
        else:
            raise Exception(f"OpenAI API error: {response.text}")
            
    def generate_claude_report(self, prompt):
        """Generate report using Anthropic Claude"""
        # Placeholder for Claude API integration
        return self.format_report("Claude integration not yet implemented. Please use OpenAI or Local LLM.")
        
    def generate_local_report(self, prompt):
        """Generate report using local LLM"""
        # This would integrate with a local LLM like LLaMA or similar
        # For now, return a template-based report
        
        report = """<h2>Geological Profile Analysis Report</h2>
        
<h3>Executive Summary</h3>
<p>This report presents an analysis of the elevation profiles collected through the dual profile viewer system.</p>

<h3>Statistical Analysis</h3>
<p>The elevation data shows significant variation across the surveyed sections, with notable features that warrant further investigation.</p>

<h3>Interpretation</h3>
<p>The terrain features suggest potential archaeological or geological significance. The elevation patterns indicate possible human modification or natural formation processes.</p>

<h3>Recommendations</h3>
<ul>
<li>Conduct detailed ground survey of identified anomalies</li>
<li>Consider geophysical investigation of subsurface features</li>
<li>Compare findings with historical records and maps</li>
</ul>

<p><em>Note: This is a template report. For AI-generated analysis, please configure OpenAI or Claude API.</em></p>"""
        
        return report
        
    def format_report(self, content):
        """Format report content as HTML"""
        # Convert markdown-style content to HTML
        html = "<html><head><style>"
        html += "body { font-family: Arial, sans-serif; line-height: 1.6; }"
        html += "h2 { color: #2c3e50; }"
        html += "h3 { color: #34495e; }"
        html += "p { margin: 10px 0; }"
        html += "ul { margin: 10px 0; padding-left: 20px; }"
        html += "</style></head><body>"
        
        # Simple markdown to HTML conversion
        lines = content.split('\n')
        for line in lines:
            if line.startswith('##'):
                html += f"<h2>{line[2:].strip()}</h2>"
            elif line.startswith('#'):
                html += f"<h3>{line[1:].strip()}</h3>"
            elif line.startswith('-') or line.startswith('*'):
                html += f"<li>{line[1:].strip()}</li>"
            elif line.strip():
                html += f"<p>{line}</p>"
                
        html += "</body></html>"
        return html
        
    def export_report(self):
        """Export report to file"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Report",
            "profile_analysis_report.html",
            "HTML Files (*.html);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            try:
                content = self.report_text.toHtml() if filename.endswith('.html') else self.report_text.toPlainText()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                QtWidgets.QMessageBox.information(self, "Success", f"Report exported to {filename}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to export report: {str(e)}")
    
    def get_report_text(self):
        """Get the generated report text"""
        return self.generated_report