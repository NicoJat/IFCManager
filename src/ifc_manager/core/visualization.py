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

    def visualize_ifc_model(self, structural_elements, filter_types=None, show_axes=True):
        """
        Visualiza modelo IFC con filtros opcionales.
        
        Args:
            structural_elements: Dict con elementos estructurales
            filter_types: Lista de tipos a mostrar (ej: ['IfcBeam', 'IfcColumn'])
            show_axes: Si mostrar ejes de elementos lineales
        """
        if not structural_elements:
            logger.warning("No structural elements to visualize")
            return go.Figure()
        
        fig = go.Figure()
        
        # Colores mejorados
        default_colors = {
            'IfcBeam': '#1f77b4',      # Azul
            'IfcColumn': '#d62728',     # Rojo
            'IfcSlab': '#2ca02c',       # Verde
            'IfcWall': '#ff7f0e',       # Naranja
            'IfcFooting': '#9467bd',    # Púrpura
            'IfcPile': '#8c564b',       # Marrón
            'IfcMember': '#e377c2',     # Rosa
        }
        
        element_counts = {}
        
        for elem_id, elem_data in structural_elements.items():
            try:
                elem_type = elem_data.get('type', 'Unknown')
                
                # Aplicar filtro si existe
                if filter_types and elem_type not in filter_types:
                    continue
                
                # Contar elementos por tipo
                element_counts[elem_type] = element_counts.get(elem_type, 0) + 1
                
                if 'geometry' not in elem_data:
                    continue

                color = default_colors.get(elem_type, '#808080')
                geom = elem_data['geometry']
                name = elem_data.get('name', '') or f"{elem_type}_{element_counts[elem_type]}"

                # Visualizar malla
                if geom.get('type') == 'mesh' and 'vertices' in geom and 'triangles' in geom:
                    vertices = np.array(geom['vertices'])
                    triangles = np.array(geom['triangles'])

                    if len(vertices) > 0 and len(triangles) > 0:
                        x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
                        
                        # Validar índices de triángulos
                        valid_triangles = triangles[np.all(triangles < len(vertices), axis=1)]
                        
                        if len(valid_triangles) > 0:
                            i, j, k = valid_triangles[:, 0], valid_triangles[:, 1], valid_triangles[:, 2]
                            
                            fig.add_trace(go.Mesh3d(
                                x=x, y=y, z=z,
                                i=i, j=j, k=k,
                                color=color,
                                opacity=0.7,
                                name=f"{elem_type} ({element_counts[elem_type]})",
                                hovertemplate=f"<b>{name}</b><br>" +
                                            f"Type: {elem_type}<br>" +
                                            f"ID: {elem_id}<br>" +
                                            "<extra></extra>",
                                showscale=False,
                                legendgroup=elem_type
                            ))

                # Visualizar línea central para elementos lineales
                if (geom.get('type') == 'line' and show_axes and 
                    'start' in geom and 'end' in geom):
                    
                    start, end = geom['start'], geom['end']
                    
                    fig.add_trace(go.Scatter3d(
                        x=[start[0], end[0]],
                        y=[start[1], end[1]],
                        z=[start[2], end[2]],
                        mode='lines+markers',
                        line=dict(color='black', width=4),
                        marker=dict(size=3, color='black'),
                        name=f"{elem_type} Axis",
                        hovertemplate=f"<b>{name} - Axis</b><br>" +
                                    f"Start: ({start[0]:.2f}, {start[1]:.2f}, {start[2]:.2f})<br>" +
                                    f"End: ({end[0]:.2f}, {end[1]:.2f}, {end[2]:.2f})<br>" +
                                    "<extra></extra>",
                        showlegend=False
                    ))
                    
            except Exception as e:
                logger.warning(f"Error visualizing element {elem_id}: {e}")
                continue

        # Configuración mejorada del layout
        fig.update_layout(
            title={
                'text': f'IFC Structural Model ({sum(element_counts.values())} elements)',
                'x': 0.5,
                'font': {'size': 16}
            },
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Z (m)',
                aspectmode='data',
                bgcolor='rgba(240,240,240,0.1)',
                xaxis=dict(backgroundcolor="white", gridcolor="lightgray"),
                yaxis=dict(backgroundcolor="white", gridcolor="lightgray"),
                zaxis=dict(backgroundcolor="white", gridcolor="lightgray"),
            ),
            legend=dict(
                title='Element Types',
                font=dict(size=10),
                itemsizing='constant',
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='gray',
                borderwidth=1
            ),
            margin=dict(l=10, r=10, t=40, b=10),
            height=600
        )
        
        # Agregar anotación con estadísticas
        stats_text = "<br>".join([f"{k}: {v}" for k, v in element_counts.items()])
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            xanchor='left', yanchor='top',
            showarrow=False,
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1
        )

        return fig

    # MÉTODO ADICIONAL: Visualización de estadísticas
    def create_statistics_plot(self, structural_elements):
        """Crea gráfico de estadísticas de elementos."""
        if not structural_elements:
            return go.Figure()
        
        # Contar elementos por tipo
        type_counts = {}
        for elem_data in structural_elements.values():
            elem_type = elem_data.get('type', 'Unknown')
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        # Crear gráfico de barras
        fig = go.Figure([go.Bar(
            x=list(type_counts.keys()),
            y=list(type_counts.values()),
            text=list(type_counts.values()),
            textposition='auto',
        )])
        
        fig.update_layout(
            title='Element Count by Type',
            xaxis_title='Element Type',
            yaxis_title='Count',
            height=400
        )
        
        return fig
