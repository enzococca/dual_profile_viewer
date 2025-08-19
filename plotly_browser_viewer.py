"""
Alternative Plotly viewer that opens visualization in the default browser
This avoids QWebEngine compatibility issues
"""

import numpy as np
import tempfile
import webbrowser
import os

try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def create_plotly_3d_visualization(profile_data_list, settings):
    """Create Plotly visualization and open in browser"""
    
    if not PLOTLY_AVAILABLE:
        return False, "Plotly is not installed"
        
    # Handle both single profile and list of profiles
    if isinstance(profile_data_list, list):
        if profile_data_list and isinstance(profile_data_list[0], list):
            profiles = profile_data_list
        else:
            profiles = [profile_data_list]
    else:
        profiles = [profile_data_list]
        
    fig = go.Figure()
    
    # Process each profile
    for i, profile_data in enumerate(profiles):
        if not profile_data:
            continue
            
        # Extract profile data
        profile_array = np.array(profile_data)
        distances = profile_array[:, 0]
        elevations = profile_array[:, 1]
        
        # Create cross-section mesh
        cross_width = settings.get('cross_width', 100)
        n_cross = 20
        
        # For cross-sections, rotate profiles
        if i == 0:
            # First profile along X axis
            x = distances
            y = np.zeros_like(distances)
            z = elevations
        else:
            # Second profile along Y axis (creating intersection)
            x = np.zeros_like(distances)
            y = distances
            z = elevations
            
        # Create surface mesh for each profile
        if i == 0:
            Y_mesh = np.linspace(-cross_width/2, cross_width/2, n_cross)
            X_mesh, Y_mesh = np.meshgrid(x, Y_mesh)
            Z_mesh = np.tile(z, (n_cross, 1))
        else:
            X_mesh = np.linspace(-cross_width/2, cross_width/2, n_cross)
            X_mesh, Y_mesh = np.meshgrid(X_mesh, y)
            Z_mesh = np.tile(z, (n_cross, 1)).T
            
        # Get valid colorscale
        colormap_mapping = {
            'terrain': 'earth',
            'viridis': 'viridis',
            'plasma': 'plasma',
            'coolwarm': 'bluered',
            'seismic': 'rdbu'
        }
        colorscale = colormap_mapping.get(settings.get('colormap', 'earth'), 'earth')
        
        # Add surface
        surface = go.Surface(
            x=X_mesh,
            y=Y_mesh,
            z=Z_mesh,
            colorscale=colorscale,
            name=f'Profile {i+1}',
            showscale=i == 0,
            opacity=0.9
        )
        fig.add_trace(surface)
        
        # Add profile lines
        fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='lines',
            line=dict(color='red' if i == 0 else 'blue', width=4),
            name=f'Profile Line {i+1}'
        ))
        
        # Add layers if requested
        if settings.get('show_layers', True):
            layer_count = settings.get('layer_count', 10)
            z_min, z_max = np.min(Z_mesh), np.max(Z_mesh)
            layer_elevations = np.linspace(z_min, z_max, layer_count)
            
            for elev in layer_elevations[1:-1]:
                fig.add_trace(go.Scatter3d(
                    x=X_mesh.flatten()[::10],  # Sample points for performance
                    y=Y_mesh.flatten()[::10],
                    z=np.full(len(X_mesh.flatten()[::10]), elev),
                    mode='markers',
                    marker=dict(size=1, color='gray', opacity=0.3),
                    name=f'Layer {elev:.1f}m',
                    showlegend=False
                ))
    
    # Configure layout
    fig.update_layout(
        title='3D Cross-Section Visualization',
        scene=dict(
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Elevation (m)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5)
        ),
        showlegend=True,
        hovermode='closest',
        width=1200,
        height=800
    )
    
    # Save to temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        # Generate complete HTML
        html_string = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')
        full_html = f"""
        <html>
        <head>
            <title>3D Cross-Section Visualization</title>
        </head>
        <body>
            {html_string}
        </body>
        </html>
        """
        f.write(full_html)
        temp_path = f.name
        
    # Open in browser
    webbrowser.open(f'file://{temp_path}')
    
    return True, "Visualization opened in browser"