"""
IFC-OpenSeesPy Linker - Convert BIM (IFC) models to structural analysis models for OpenSeesPy.

This package provides tools to parse IFC files, extract structural elements,
convert them to OpenSeesPy models, and visualize the results.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# src/ifc_openseespy_linker/core/__init__.py
from .ifc_parser import IFCParser
from .opensees_converter import OpenSeesConverter
from .visualization import ModelVisualizer

# Convenience class that integrates all components
class IFCtoOpenSeesConverter:
    """
    Main converter class that integrates parsing, conversion, and visualization.
    
    This class serves as the primary interface for the library, combining the
    functionality of the IFCParser, OpenSeesConverter, and ModelVisualizer.
    
    Example:
        >>> converter = IFCtoOpenSeesConverter("model.ifc")
        >>> converter.load_ifc()
        >>> converter.extract_structural_elements()
        >>> converter.create_opensees_model()
        >>> converter.run_analysis()
        >>> converter.visualize_results()
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
        
        self.structural_elements = self.parser.extract_structural_elements()
        self.parser.extract_geometry()
        
        # Initialize converter with extracted elements
        self.converter = OpenSeesConverter(self.structural_elements)
        
        return self.structural_elements
    
    def create_opensees_model(self):
        """Create an OpenSees model from the extracted structural elements."""
        if not self.converter:
            if not self.structural_elements:
                raise ValueError("No structural elements extracted. Call extract_structural_elements() first.")
            self.converter = OpenSeesConverter(self.structural_elements)
        
        return self.converter.create_model()
    
    def run_analysis(self, analysis_type="static"):
        """Run structural analysis on the created OpenSees model."""
        if not self.converter:
            raise ValueError("No OpenSees model created. Call create_opensees_model() first.")
        
        self.analysis_results = self.converter.run_analysis(analysis_type)
        return self.analysis_results
    
    def visualize_model(self):
        """Visualize the 3D model from IFC data."""
        if not self.parser:
            raise ValueError("No IFC parser initialized. Call load_ifc() first.")
        
        return self.visualizer.visualize_ifc_model(self.structural_elements)
    
    def visualize_results(self, result_type="displacements", scale_factor=10):
        """Visualize analysis results."""
        if not self.analysis_results:
            raise ValueError("No analysis results available. Call run_analysis() first.")
        
        return self.visualizer.visualize_results(
            self.structural_elements, 
            self.analysis_results, 
            result_type, 
            scale_factor
        )