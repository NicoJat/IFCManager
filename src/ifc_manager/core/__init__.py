"""
IFCManager - Analyse IFC files simplifying IFCOpenshell
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .ifc_parser import IFCParser
from .visualization import ModelVisualizer


# Convenience class that integrates all components
class IFCManager:
    """
    Main converter class that integrates parsing, conversion, and visualization.
    
    This class serves as the primary interface for the library, combining the
    functionality of the IFCParser, and ModelVisualizer.
    """
    
    def __init__(self, ifc_file_path=None):
        """Initialize the converter with an optional IFC file path."""
        self.ifc_file_path = ifc_file_path
        self.parser = IFCParser(ifc_file_path) if ifc_file_path else None
        self.converter = None
        self.visualizer = ModelVisualizer()
        self.structural_elements = {}
        self.analysis_results = None
    
    def load_ifc(self, ifc_file_path=None):
        """Load an IFC file."""
        if ifc_file_path:
            self.ifc_file_path = ifc_file_path
            self.parser = IFCParser(ifc_file_path)
        
        if not self.parser:
            raise ValueError("No IFC file path provided.")
        
        return self.parser.load_ifc_file()
    
    def extract_structural_elements(self):
        """Extract structural elements from the loaded IFC file."""
        if not self.parser:
            raise ValueError("No IFC parser initialized. Call load_ifc() first.")
        
        # Extraer elementos
        self.structural_elements = self.parser.extract_structural_elements()
        
        # Extraer geometría
        self.parser.extract_geometry()
        
        # NUEVO: Calcular propiedades automáticamente
        self.parser.calculate_element_properties()
        
        return self.structural_elements

    def visualize_model(self, filter_types=None, show_axes=True):
        """Visualize the 3D model from IFC data with optional filters."""
        if not self.parser:
            raise ValueError("No IFC parser initialized. Call load_ifc() first.")
        
        if not self.structural_elements:
            logger.warning("No structural elements found. Call extract_structural_elements() first.")
            return go.Figure()
        
        return self.visualizer.visualize_ifc_model(
            self.structural_elements, 
            filter_types=filter_types,
            show_axes=show_axes
        )

    def get_statistics(self):
        """Get model statistics."""
        if not self.structural_elements:
            return {}
        
        stats = {
            'total_elements': len(self.structural_elements),
            'by_type': {},
            'by_material': {}
        }
        
        # Estadísticas por tipo
        for elem_data in self.structural_elements.values():
            elem_type = elem_data.get('type', 'Unknown')
            stats['by_type'][elem_type] = stats['by_type'].get(elem_type, 0) + 1
        
        # Estadísticas por material (si existen)
        if hasattr(self.parser, 'count_properties_by_material'):
            stats['by_material'] = self.parser.count_properties_by_material()
        
        return stats

    def export_elements_summary(self, filename=None):
        """Export elements summary to CSV format."""
        import csv
        import io
        
        if not self.structural_elements:
            return None
        
        # Crear datos para CSV
        csv_data = []
        for elem_id, elem_data in self.structural_elements.items():
            row = {
                'ID': elem_id,
                'Name': elem_data.get('name', ''),
                'Type': elem_data.get('type', ''),
                'Volume': elem_data.get('volume', 0),
                'Area': elem_data.get('area', 0),
                'Length': elem_data.get('length', 0),
            }
            
            # Agregar material si existe
            if 'material' in elem_data and elem_data['material']:
                materials = list(elem_data['material'].keys())
                row['Material'] = ', '.join(materials)
            else:
                row['Material'] = ''
            
            csv_data.append(row)
        
        # Si no se especifica filename, retornar como string
        if not filename:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
            return output.getvalue()
        
        # Guardar en archivo
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
        
        return f"Summary exported to {filename}"

    def validate_model(self):
        """Validate the loaded model for common issues."""
        issues = []
        
        if not self.structural_elements:
            issues.append("No structural elements found")
            return issues
        
        for elem_id, elem_data in self.structural_elements.items():
            # Verificar elementos sin geometría
            if 'geometry' not in elem_data:
                issues.append(f"Element {elem_id} has no geometry")
            
            # Verificar elementos sin material
            if 'material' not in elem_data or not elem_data['material']:
                issues.append(f"Element {elem_id} ({elem_data.get('type', 'Unknown')}) has no material")
            
            # Verificar volumen/área cero
            if elem_data.get('volume', 0) == 0:
                issues.append(f"Element {elem_id} has zero volume")
        
        return issues