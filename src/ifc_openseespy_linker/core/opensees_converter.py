"""
OpenSeesPy Converter Module

Converts extracted structural elements into OpenSeesPy models and runs analysis.
"""

import openseespy.opensees as ops
import math
import logging

logger = logging.getLogger(__name__)

class OpenSeesConverter:
    """Converts IFC structural elements to OpenSeesPy models and runs analysis."""
    
    def __init__(self, structural_elements):
        """
        Initialize converter with structural elements.
        
        Args:
            structural_elements (dict): Structural elements from IFCParser
        """
        self.structural_elements = structural_elements
        self.nodes = {}
        self.elements = {}
        self.materials_defined = False
        self.model_created = False
    
    def create_model(self):
        """Creates OpenSees model from structural elements."""
        if not self.structural_elements:
            logger.error("No structural elements to convert")
            return False
            
        try:
            # Initialize OpenSees model
            ops.wipe()
            ops.model('basic', '-ndm', 3, '-ndf', 6)
            
            # Define materials and sections
            self._define_materials()
            
            # Create nodes and elements
            self._create_nodes()
            self._create_elements()
            
            # Apply boundary conditions
            self._apply_boundary_conditions()
            
            # Apply loads
            self._apply_loads()
            
            self.model_created = True
            return True
            
        except Exception as e:
            logger.error(f"Error creating OpenSees model: {e}")
            return False
    
    def _define_materials(self):
        """Defines materials and sections in OpenSees."""
        # Default steel material properties
        E = 200e9  # Pa
        G = 76.92e9 # Pa
        density = 7850  # kg/m³
        
        # Define uniaxial material
        ops.uniaxialMaterial('Elastic', 1, E)
        
        # Define section properties (simplified)
        self.default_section = {
            'A': 0.1,    # m²
            'Iz': 0.001, # m⁴
            'Iy': 0.001, # m⁴
            'J': 0.0001 # m⁴
        }
        
        # Define geometric transformation
        ops.geomTransf('Linear', 1, 1, 0, 0)
        self.materials_defined = True
    
    def _create_nodes(self):
        """Creates nodes from structural element geometry."""
        node_id = 1
        defined_coords = {}
        
        for elem_id, elem_data in self.structural_elements.items():
            if elem_data['geometry']['type'] == 'line':
                start = elem_data['geometry']['start']
                end = elem_data['geometry']['end']
                
                for coords in [start, end]:
                    coord_tuple = tuple(coords)
                    if coord_tuple not in defined_coords:
                        ops.node(node_id, *coords)
                        defined_coords[coord_tuple] = node_id
                        self.nodes[node_id] = coords
                        node_id += 1
        
        logger.info(f"Created {len(self.nodes)} nodes")
    
    def _create_elements(self):
        """Creates beam-column elements from line geometry."""
        element_id = 1
        
        for elem_id, elem_data in self.structural_elements.items():
            if elem_data['type'] in ['IfcBeam', 'IfcColumn', 'IfcMember']:
                if elem_data['geometry']['type'] == 'line':
                    start = elem_data['geometry']['start']
                    end = elem_data['geometry']['end']
                    
                    # Find node IDs
                    start_node = self._find_node(start)
                    end_node = self._find_node(end)
                    
                    if start_node and end_node:
                        # Get section properties from profile
                        section = self._get_section_properties(elem_data)
                        
                        # Create element
                        ops.element('elasticBeamColumn', element_id, 
                                    start_node, end_node,
                                    section['A'], 200e9,  # E
                                    76.92e9,               # G
                                    section['J'],
                                    section['Iy'],
                                    section['Iz'],
                                    1)  # transfTag
                        
                        self.elements[element_id] = {
                            'nodes': [start_node, end_node],
                            'type': elem_data['type']
                        }
                        element_id += 1
        
        logger.info(f"Created {len(self.elements)} elements")
    
    def _find_node(self, coords):
        """Finds node ID matching coordinates."""
        target = tuple(coords)
        for node_id, node_coords in self.nodes.items():
            if all(abs(a - b) < 1e-3 for a, b in zip(node_coords, target)):
                return node_id
        return None
    
    def _get_section_properties(self, elem_data):
        """Extracts section properties from element data."""
        section = self.default_section.copy()
        
        if 'profile' in elem_data and elem_data['profile']:
            profile = elem_data['profile']
            
            if profile['shape'] == 'rectangular':
                b = profile.get('width', 0.3)
                h = profile.get('height', 0.5)
                section['A'] = b * h
                section['Iz'] = b * h**3 / 12
                section['Iy'] = h * b**3 / 12
                section['J'] = (b*h**3 + h*b**3)/12
                
            elif profile['shape'] == 'circular':
                r = profile.get('radius', 0.2)
                section['A'] = math.pi * r**2
                section['Iz'] = section['Iy'] = math.pi * r**4 / 4
                section['J'] = math.pi * r**4 / 2
                
        return section
    
    def _apply_boundary_conditions(self):
        """Applies fixed boundary conditions at base nodes."""
        min_z = min(coords[2] for coords in self.nodes.values())
        base_nodes = [
            node_id for node_id, coords in self.nodes.items()
            if abs(coords[2] - min_z) < 0.001
        ]
        
        for node_id in base_nodes:
            ops.fix(node_id, 1, 1, 1, 1, 1, 1)
        
        logger.info(f"Fixed {len(base_nodes)} base nodes")
    
    def _apply_loads(self):
        """Applies gravity loads as uniform loads."""
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)
        
        g = 9.81  # m/s²
        for elem_id, elem in self.elements.items():
            A = self._get_section_properties(elem)['A']
            density = 7850  # kg/m³
            w = -A * density * g  # N/m
            
            ops.eleLoad('-ele', elem_id, '-type', '-beamUniform', 0, 0, w)
        
        logger.info("Applied gravity loads")
    
    def run_analysis(self, analysis_type='static'):
        """Runs structural analysis and returns results."""
        if not self.model_created:
            logger.error("Model not created. Call create_model() first.")
            return None
            
        try:
            # Setup analysis
            ops.system('BandSPD')
            ops.numberer('RCM')
            ops.constraints('Plain')
            ops.integrator('LoadControl', 1.0)
            ops.algorithm('Linear')
            ops.analysis('Static')
            
            # Run analysis
            results = {'displacements': {}}
            ops.analyze(1)
            
            # Get displacements
            for node_id in self.nodes:
                disp = ops.nodeDisp(node_id)
                results['displacements'][node_id] = {
                    'dx': disp[0],
                    'dy': disp[1],
                    'dz': disp[2]
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return None