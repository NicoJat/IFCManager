"""
Visualization Module

Handles 3D visualization of IFC models and analysis results.
"""

import plotly.graph_objects as go
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ModelVisualizer:
    """Handles visualization of IFC models and analysis results."""

    def visualize_ifc_model(self, structural_elements):
        """Visualizes IFC model using Plotly."""
        fig = go.Figure()

        default_colors = {
            'IfcBeam': 'blue',
            'IfcColumn': 'red',
            'IfcSlab': 'green',
            'IfcWall': 'orange',
            'IfcFooting': 'gray',
        }

        for elem_id, elem_data in structural_elements.items():
            try:
                if 'geometry' not in elem_data:
                    continue

                color = default_colors.get(elem_data['type'], 'lightgray')
                geom = elem_data['geometry']

                # Dibujar malla
                if geom.get('type', 'mesh') == 'mesh':
                    vertices = np.array(geom['vertices'])
                    triangles = np.array(geom['triangles'])

                    if vertices.shape[0] == 0 or triangles.shape[0] == 0:
                        continue
                    
                    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
                    i, j, k = triangles[:, 0], triangles[:, 1], triangles[:, 2]

                    fig.add_trace(go.Mesh3d(
                        x=x, y=y, z=z,
                        i=i, j=j, k=k,
                        color=color,
                        opacity=0.5,
                        name=elem_data['type'],
                        showscale=False
                    ))

                # Dibujar eje si existe
                if 'axis_line' in geom:
                    start = geom['axis_line']['start']
                    end = geom['axis_line']['end']
                    fig.add_trace(go.Scatter3d(
                        x=[start[0], end[0]],
                        y=[start[1], end[1]],
                        z=[start[2], end[2]],
                        mode='lines',
                        line=dict(color='black', width=5),
                        name=f'{elem_data["type"]} Axis',
                        showlegend=False
                    ))
            except Exception as e:
                logger.warning(f"Error visualizing element {elem_id}: {e}")

        fig.update_layout(
            title='IFC Structural Model',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='data',
                bgcolor='white',
            ),
            legend=dict(
                title='Element Types',
                font=dict(size=10),
                itemsizing='constant'
            ),
            margin=dict(l=10, r=10, t=30, b=10),
        )

        return fig
