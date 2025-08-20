# -*- coding: utf-8 -*-
"""
Alternative plot generator using only matplotlib
Avoids Kaleido/Chrome issues
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class PlotGenerator:
    """Generate plots using matplotlib for layouts"""
    
    @staticmethod
    def generate_profile_plot(profile_data, output_path, dpi=300):
        """Generate a profile plot image using matplotlib"""
        
        # Create figure with 4 subplots as requested
        fig = plt.figure(figsize=(12, 8))
        
        # Extract data
        profile1 = profile_data['profile1']
        profile2 = profile_data['profile2']
        dem1_name = profile_data.get('dem1_name', 'DEM')
        
        # Calculate differences
        diff = np.array(profile1['elevations']) - np.array(profile2['elevations'])
        
        # 1. Top left - Overlapped profiles
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(profile1['distances'], profile1['elevations'], 'r-', 
                linewidth=2, label=f"A-A' ({dem1_name})")
        ax1.plot(profile2['distances'], profile2['elevations'], 'b-', 
                linewidth=2, label=f"B-B' ({dem1_name})")
        
        # Add comparison DEMs if available
        if profile_data.get('profile1_dem2'):
            profile1_dem2 = profile_data['profile1_dem2']
            profile2_dem2 = profile_data['profile2_dem2']
            dem2_name = profile_data.get('dem2_name', 'DEM2')
            
            ax1.plot(profile1_dem2['distances'], profile1_dem2['elevations'], 
                    'orange', linewidth=2, linestyle='--', 
                    label=f"A-A' ({dem2_name})")
            ax1.plot(profile2_dem2['distances'], profile2_dem2['elevations'], 
                    'lightgreen', linewidth=2, linestyle='--', 
                    label=f"B-B' ({dem2_name})")
        
        ax1.set_title('Overlapped Profiles', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Elevation (m)')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best', fontsize=8)
        
        # 2. Top right - Elevation differences
        ax2 = plt.subplot(2, 2, 2)
        ax2.fill_between(profile1['distances'], diff, 0, 
                        where=(diff >= 0), color='green', alpha=0.3, 
                        label='A > B')
        ax2.fill_between(profile1['distances'], diff, 0, 
                        where=(diff < 0), color='red', alpha=0.3, 
                        label='A < B')
        ax2.plot(profile1['distances'], diff, 'g-', linewidth=2)
        ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax2.set_title('Elevation Differences (A-B)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Difference (m)')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='best', fontsize=8)
        
        # 3. Bottom left - Profile A-A'
        ax3 = plt.subplot(2, 2, 3)
        ax3.plot(profile1['distances'], profile1['elevations'], 'r-', 
                linewidth=2, label=f"{dem1_name}")
        if profile_data.get('profile1_dem2'):
            ax3.plot(profile1_dem2['distances'], profile1_dem2['elevations'], 
                    'orange', linewidth=2, linestyle='--', 
                    label=f"{dem2_name}")
        ax3.set_title("Profile A-A'", fontsize=12, fontweight='bold')
        ax3.set_xlabel('Distance (m)')
        ax3.set_ylabel('Elevation (m)')
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='best', fontsize=8)
        
        # 4. Bottom right - Profile B-B'
        ax4 = plt.subplot(2, 2, 4)
        ax4.plot(profile2['distances'], profile2['elevations'], 'b-', 
                linewidth=2, label=f"{dem1_name}")
        if profile_data.get('profile2_dem2'):
            ax4.plot(profile2_dem2['distances'], profile2_dem2['elevations'], 
                    'lightgreen', linewidth=2, linestyle='--', 
                    label=f"{dem2_name}")
        ax4.set_title("Profile B-B'", fontsize=12, fontweight='bold')
        ax4.set_xlabel('Distance (m)')
        ax4.set_ylabel('Elevation (m)')
        ax4.grid(True, alpha=0.3)
        ax4.legend(loc='best', fontsize=8)
        
        # Add main title
        fig.suptitle('Elevation Profile Analysis', fontsize=14, fontweight='bold')
        
        # Add timestamp
        fig.text(0.99, 0.01, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                ha='right', va='bottom', fontsize=8, alpha=0.5)
        
        # Adjust layout
        plt.tight_layout(rect=[0, 0.02, 1, 0.96])
        
        # Save figure
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        
        return True
    
    @staticmethod
    def generate_simple_profile(profile_data, output_path, dpi=150):
        """Generate a simple profile plot for quick preview"""
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        
        # Extract data
        profile1 = profile_data['profile1']
        profile2 = profile_data['profile2']
        
        # Top plot - Profile A-A'
        ax1.plot(profile1['distances'], profile1['elevations'], 'r-', linewidth=2)
        ax1.set_title("Profile A-A'")
        ax1.set_ylabel('Elevation (m)')
        ax1.grid(True, alpha=0.3)
        
        # Bottom plot - Profile B-B'
        ax2.plot(profile2['distances'], profile2['elevations'], 'b-', linewidth=2)
        ax2.set_title("Profile B-B'")
        ax2.set_xlabel('Distance (m)')
        ax2.set_ylabel('Elevation (m)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        
        return True