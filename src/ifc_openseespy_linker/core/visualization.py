"""
Visualization Module

Handles 3D visualization of IFC models and analysis results.
"""

import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import math
import logging

logger = logging.getLogger(__name__)

class ModelVisualizer:
    """Handles visualization of IFC models and analysis results."""
    
    def visualize_ifc_model(self, structural_elements):
        """Visualizes IFC model using Plotly."""
        fig = go.Figure()
        colors = {
            'IfcBeam': 'blue',
            'IfcColumn': 'red',
            'IfcSlab': 'green',
            'IfcWall': 'orange',
            'default': 'gray'
        }

        for elem_id, elem_data in structural_elements.items():
            if 'geometry' not in elem_data:
                continue
                
            color = colors.get(elem_data['type'], colors['default'])
            geom = elem_data['geometry']
            
            if geom['type'] == 'mesh':
                vertices = np.array(geom['vertices'])
                triangles = np.array(geom['triangles'])
                
                if len(vertices) > 0 and len(triangles) > 0:
                    x, y, z = vertices[:,0], vertices[:,1], vertices[:,2]
                    i, j, k = triangles[:,0], triangles[:,1], triangles[:,2]
                    
                    fig.add_trace(go.Mesh3d(
                        x=x, y=y, z=z,
                        i=i, j=j, k=k,
                        color=color,
                        opacity=0.6,
                        name=elem_data['type']
                    ))
                    
        fig.update_layout(
            scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
            title='IFC Structural Model'
        )
        fig.show()
        return fig
    
    def visualize_results(self, structural_elements, results, result_type='displacements', scale_factor=10):
        """Visualizes analysis results using Matplotlib."""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot original and displaced shapes
        self._plot_original_model(ax, structural_elements)
        self._plot_displacements(ax, structural_elements, results, scale_factor)
        
        # Add colorbar
        max_disp = max(math.sqrt(d['dx']**2 + d['dy']**2 + d['dz']**2) 
                    for d in results['displacements'].values())
        norm = plt.Normalize(0, max_disp)
        sm = cm.ScalarMappable(norm=norm, cmap='jet')
        sm.set_array([])
        
        cbar = fig.colorbar(sm, ax=ax, shrink=0.5)
        cbar.set_label('Displacement Magnitude (m)')
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.title(f"Structural Analysis Results (Scale Factor: {scale_factor})")
        plt.tight_layout()
        plt.show()
        return fig, ax
    
    def _plot_original_model(self, ax, structural_elements):
        """Plots original model in light gray."""
        for elem_id, elem_data in structural_elements.items():
            geom = elem_data.get('geometry', {})
            if geom.get('type') == 'line':
                start = geom['start']
                end = geom['end']
                ax.plot(
                    [start[0], end[0]],
                    [start[1], end[1]], 
                    [start[2], end[2]],
                    color='lightgray', 
                    alpha=0.4
                )
    
    def _plot_displacements(self, ax, structural_elements, results, scale_factor):
        """Plots displaced shape with color mapping."""
        cmap = cm.get_cmap('jet')
        
        for elem_id, elem_data in structural_elements.items():
            geom = elem_data.get('geometry', {})
            if geom.get('type') == 'line' and 'nodes' in elem_data:
                start_node = elem_data['nodes'][0]
                end_node = elem_data['nodes'][1]
                
                disp1 = results['displacements'].get(start_node, {'dx':0, 'dy':0, 'dz':0})
                disp2 = results['displacements'].get(end_node, {'dx':0, 'dy':0, 'dz':0})
                
                # Calculate displaced coordinates
                start = geom['start']
                end = geom['end']
                start_disp = [
                    start[0] + disp1['dx']*scale_factor,
                    start[1] + disp1['dy']*scale_factor,
                    start[2] + disp1['dz']*scale_factor
                ]
                end_disp = [
                    end[0] + disp2['dx']*scale_factor,
                    end[1] + disp2['dy']*scale_factor,
                    end[2] + disp2['dz']*scale_factor
                ]
                
                # Get color based on average displacement
                avg_disp = (math.sqrt(disp1['dx']**2 + disp1['dy']**2 + disp1['dz']**2) +
                          math.sqrt(disp2['dx']**2 + disp2['dy']**2 + disp2['dz']**2)) / 2
                color = cmap(avg_disp / max(1e-9, avg_disp))
                
                ax.plot(
                    [start_disp[0], end_disp[0]],
                    [start_disp[1], end_disp[1]],
                    [start_disp[2], end_disp[2]],
                    color=color,
                    linewidth=2
                )