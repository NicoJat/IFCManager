"""
IFC Parser module for extracting structural elements from IFC files.

This module handles loading and parsing IFC files to extract structural elements,
their properties, materials, and geometry.
"""

import os
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element as Element
import ifcopenshell.util.pset as Pset
import ifcopenshell.util.placement as Placement
import numpy as np
import math
import logging

# Configure logging
logger = logging.getLogger(__name__)

class IFCParser:
    """
    Parser for IFC files to extract structural elements.
    
    This class handles loading an IFC file, extracting structural elements
    (beams, columns, walls, slabs, etc.), their properties, materials,
    and geometric representations.
    """
    
    def __init__(self, ifc_file_path=None):
        """
        Initialize the IFC parser.
        
        Args:
            ifc_file_path (str, optional): Path to the IFC file to parse.
        """
        self.ifc_file_path = ifc_file_path
        self.ifc_model = None
        self.settings = None
        self.structural_elements = {}
        self.materials = {}
        self.nodes = {}
        self.elements = {}
    
    def load_ifc_file(self):
        """
        Load the IFC file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.ifc_file_path:
            logger.error("No IFC file path provided.")
            return False
        
        if not os.path.exists(self.ifc_file_path):
            logger.error(f"IFC file not found: {self.ifc_file_path}")
            return False
        
        try:
            logger.info(f"Loading IFC file: {self.ifc_file_path}")
            self.ifc_model = ifcopenshell.open(self.ifc_file_path)
            logger.info(f"IFC file loaded successfully with {len(self.ifc_model.by_type('IfcProduct'))} products")
            
            # Initialize settings for geometry processing
            self.settings = ifcopenshell.geom.settings()
            self.settings.set(self.settings.USE_WORLD_COORDS, True)
            
            return True
        except Exception as e:
            logger.error(f"Error loading IFC file: {e}")
            return False
    
    def extract_structural_elements(self):
        """
        Extract structural elements from the loaded IFC model.
        
        Returns:
            dict: Dictionary of structural elements keyed by their GlobalId.
        """
        if not self.ifc_model:
            logger.error("No IFC model loaded. Call load_ifc_file() first.")
            return {}
        
        # Structural element types to extract
        structural_types = [
            'IfcBeam', 'IfcColumn', 'IfcSlab', 'IfcWall',
            'IfcFooting', 'IfcPile', 'IfcMember'
        ]
        
        logger.info("Extracting structural elements...")
        for element_type in structural_types:
            elements = self.ifc_model.by_type(element_type)
            logger.info(f"Found {len(elements)} elements of type {element_type}")
            
            for element in elements:
                # Extract basic properties
                element_data = {
                    'id': element.GlobalId,
                    'name': element.Name if hasattr(element, 'Name') and element.Name else '',
                    'type': element.is_a(),
                    'geometry': None,
                    'material': None,
                    'profile': None,
                    'properties': {}
                }
                
                # Extract element properties
                psets = ifcopenshell.util.element.get_psets(element)
                for pset_name, pset_data in psets.items():
                    for prop_name, prop_value in pset_data.items():
                        element_data['properties'][f"{pset_name}.{prop_name}"] = prop_value
                
                # Extract material information
                material = self._extract_material(element)
                if material:
                    element_data['material'] = material
                
                # Extract profile information for linear elements
                if element_type in ['IfcBeam', 'IfcColumn', 'IfcMember']:
                    element_data['profile'] = self._extract_profile(element)
                
                # Store the element
                self.structural_elements[element.GlobalId] = element_data
        
        logger.info(f"Extracted {len(self.structural_elements)} structural elements in total")
        return self.structural_elements
    
    def _extract_material(self, element):
        """
        Extract material information for an IFC element.
        
        Args:
            element (IfcProduct): The IFC element to extract material from.
            
        Returns:
            dict: Dictionary of material properties, or None if not found.
        """
        try:
            materials = {}
            
            # Try different mechanisms to get material
            rel_associates = element.HasAssociations
            for rel in rel_associates:
                if rel.is_a('IfcRelAssociatesMaterial'):
                    material_select = rel.RelatingMaterial
                    
                    # Direct material
                    if material_select.is_a('IfcMaterial'):
                        material = material_select
                        materials[material.Name] = {
                            'name': material.Name,
                            'type': 'material',
                            'properties': {}
                        }
                    
                    # Material list
                    elif material_select.is_a('IfcMaterialList'):
                        for material in material_select.Materials:
                            materials[material.Name] = {
                                'name': material.Name,
                                'type': 'material',
                                'properties': {}
                            }
                    
                    # Material layers
                    elif material_select.is_a('IfcMaterialLayerSetUsage'):
                        material_layers = material_select.ForLayerSet.MaterialLayers
                        for layer in material_layers:
                            material = layer.Material
                            materials[material.Name] = {
                                'name': material.Name,
                                'type': 'layer',
                                'thickness': layer.LayerThickness,
                                'properties': {}
                            }
                    
                    # Material profile set
                    elif material_select.is_a('IfcMaterialProfileSetUsage'):
                        material_profiles = material_select.ForProfileSet.MaterialProfiles
                        for profile in material_profiles:
                            material = profile.Material
                            materials[material.Name] = {
                                'name': material.Name,
                                'type': 'profile',
                                'profile': profile.Profile.ProfileName if profile.Profile and hasattr(profile.Profile, 'ProfileName') else None,
                                'properties': {}
                            }
            
            # Extract material properties
            for material_name in materials:
                material_objs = self.ifc_model.by_type('IfcMaterial')
                for mat in material_objs:
                    if mat.Name == material_name:
                        try:
                            # Try to extract material properties
                            mat_props = ifcopenshell.util.element.get_psets(mat)
                            for pset_name, props in mat_props.items():
                                for prop_name, prop_value in props.items():
                                    materials[material_name]['properties'][f"{pset_name}.{prop_name}"] = prop_value
                        except Exception as e:
                            logger.warning(f"Could not extract properties for material {material_name}: {e}")
            
            return materials if materials else None
        except Exception as e:
            logger.warning(f"Error extracting material for element {element.GlobalId}: {e}")
            return None
    
    def _extract_profile(self, element):
        """
        Extract profile information for a linear structural element.
        
        Args:
            element (IfcProduct): The IFC element to extract profile from.
            
        Returns:
            dict: Dictionary of profile properties, or None if not found.
        """
        try:
            profile_data = {}
            
            # Check for representation
            if not element.Representation:
                return None
            
            # Look for profile definition in representations
            representations = element.Representation.Representations
            for rep in representations:
                if rep.RepresentationType == 'SweptSolid':
                    for item in rep.Items:
                        if item.is_a('IfcExtrudedAreaSolid'):
                            # Get the profile
                            profile = item.SweptArea
                            
                            profile_data['type'] = profile.is_a()
                            profile_data['depth'] = getattr(profile, 'Depth', 0)
                            profile_data['width'] = getattr(profile, 'Width', 0)
                            profile_data['area'] = getattr(profile, 'Area', 0)
                            
                            # Extract parameters specific to profile type
                            if profile.is_a('IfcRectangleProfileDef'):
                                profile_data['shape'] = 'rectangular'
                                profile_data['height'] = profile.YDim
                                profile_data['width'] = profile.XDim
                            elif profile.is_a('IfcCircleProfileDef'):
                                profile_data['shape'] = 'circular'
                                profile_data['radius'] = profile.Radius
                            elif profile.is_a('IfcIShapeProfileDef'):
                                profile_data['shape'] = 'I-shape'
                                profile_data['height'] = profile.OverallDepth
                                profile_data['width'] = profile.OverallWidth
                                profile_data['web_thickness'] = profile.WebThickness
                                profile_data['flange_thickness'] = profile.FlangeThickness
                            
                            # Get extrusion direction
                            profile_data['extrusion_direction'] = [
                                item.ExtrudedDirection.DirectionRatios[0],
                                item.ExtrudedDirection.DirectionRatios[1],
                                item.ExtrudedDirection.DirectionRatios[2]
                            ]
                            profile_data['extrusion_depth'] = item.Depth
                            
                            return profile_data
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting profile for element {element.GlobalId}: {e}")
            return None
    
    def extract_geometry(self):
        """
        Extract geometry from structural elements.
        
        Updates the structural_elements dictionary with geometry data.
        
        Returns:
            dict: Updated structural_elements dictionary.
        """
        if not self.ifc_model:
            logger.error("No IFC model loaded. Call load_ifc_file() first.")
            return {}
        
        logger.info("Extracting geometry for structural elements...")
        
        for element_id, element_data in self.structural_elements.items():
            try:
                # Find the element in the IFC model
                element = self.ifc_model.by_guid(element_id)
                
                # Process geometry with ifcopenshell.geom
                try:
                    shape = ifcopenshell.geom.create_shape(self.settings, element)
                    
                    # Extract vertices
                    verts = shape.geometry.verts
                    faces = shape.geometry.faces
                    
                    # Convert to more useful format
                    vertices = []
                    for i in range(0, len(verts), 3):
                        vertices.append([verts[i], verts[i+1], verts[i+2]])
                    
                    # Convert face indices to triples (for triangles)
                    triangles = []
                    for i in range(0, len(faces), 3):
                        triangles.append([faces[i], faces[i+1], faces[i+2]])
                    
                    # For linear elements (beams, columns), extract axis line
                    if element_data['type'] in ['IfcBeam', 'IfcColumn', 'IfcMember']:
                        # Calculate axis line based on section centroid
                        # and extrusion direction
                        if element_data['profile']:
                            # Get element placement
                            placement = element.ObjectPlacement
                            matrix = Placement.get_local_placement(placement)
                            
                            # Transformation matrix (rotation + translation)
                            location = [matrix[0][3], matrix[1][3], matrix[2][3]]
                            
                            # Extrusion direction (transformed by matrix)
                            if 'extrusion_direction' in element_data['profile']:
                                dir_x = element_data['profile']['extrusion_direction'][0]
                                dir_y = element_data['profile']['extrusion_direction'][1]
                                dir_z = element_data['profile']['extrusion_direction'][2]
                                
                                # Apply only rotation part of matrix
                                direction = [
                                    matrix[0][0]*dir_x + matrix[0][1]*dir_y + matrix[0][2]*dir_z,
                                    matrix[1][0]*dir_x + matrix[1][1]*dir_y + matrix[1][2]*dir_z,
                                    matrix[2][0]*dir_x + matrix[2][1]*dir_y + matrix[2][2]*dir_z
                                ]
                                
                                # Normalize direction
                                length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
                                if length > 0:
                                    direction = [d/length for d in direction]
                                
                                # Extrusion depth
                                extrusion_depth = element_data['profile']['extrusion_depth']
                                
                                # Calculate endpoint
                                endpoint = [
                                    location[0] + direction[0] * extrusion_depth,
                                    location[1] + direction[1] * extrusion_depth,
                                    location[2] + direction[2] * extrusion_depth
                                ]
                                
                                # Save axis line
                                element_data['geometry'] = {
                                    'type': 'line',
                                    'start': location,
                                    'end': endpoint,
                                    'vertices': vertices,
                                    'triangles': triangles
                                }
                            else:
                                element_data['geometry'] = {
                                    'type': 'mesh',
                                    'vertices': vertices,
                                    'triangles': triangles
                                }
                        else:
                            element_data['geometry'] = {
                                'type': 'mesh',
                                'vertices': vertices,
                                'triangles': triangles
                            }
                    
                    # For surface elements (slabs, walls)
                    elif element_data['type'] in ['IfcSlab', 'IfcWall']:
                        # Save as mesh
                        element_data['geometry'] = {
                            'type': 'mesh',
                            'vertices': vertices,
                            'triangles': triangles
                        }
                    
                    # For other elements
                    else:
                        element_data['geometry'] = {
                            'type': 'mesh',
                            'vertices': vertices,
                            'triangles': triangles
                        }
                
                except RuntimeError as e:
                    logger.warning(f"Error processing geometry for element {element_id}: {e}")
                    continue
            
            except Exception as e:
                logger.warning(f"Error extracting geometry for element {element_id}: {e}")
                continue
        
        logger.info("Geometry extraction completed")
        return self.structural_elements
    
    def get_material_properties(self, material_id):
        """
        Get properties for a specific material.
        
        Args:
            material_id (str): Material identifier.
            
        Returns:
            dict: Material properties.
        """
        return self.materials.get(material_id, {})
    
    def get_structural_element(self, element_id):
        """
        Get data for a specific structural element.
        
        Args:
            element_id (str): Element identifier (GlobalId).
            
        Returns:
            dict: Element data.
        """
        return self.structural_elements.get(element_id, {})
    
    def get_element_by_name(self, name):
        """
        Get elements by name.
        
        Args:
            name (str): Element name to search for.
            
        Returns:
            list: List of elements with matching name.
        """
        return [elem for elem_id, elem in self.structural_elements.items() 
                if 'name' in elem and elem['name'] == name]
    
    def get_elements_by_type(self, element_type):
        """
        Get elements by type.
        
        Args:
            element_type (str): Element type to filter by (e.g., 'IfcBeam').
            
        Returns:
            dict: Dictionary of elements of the specified type.
        """
        return {elem_id: elem for elem_id, elem in self.structural_elements.items() 
                if elem['type'] == element_type}
    
    
    def calculate_element_properties(self):
        for element_id, element_data in self.structural_elements.items():
            if 'geometry' in element_data:
                geom = element_data['geometry']
                if geom['type'] == 'esh':
                    # Calcula el volumen y área del elemento
                    vertices = np.array(geom['vertices'])
                    triangles = np.array(geom['triangles'])
                    volume = self.calculate_mesh_volume(vertices, triangles)
                    area = self.calculate_mesh_area(vertices, triangles)
                    element_data['volume'] = volume
                    element_data['area'] = area
                elif geom['type'] == 'line':
                    # Calcula el volumen y área del elemento lineal
                    start = geom['start']
                    end = geom['end']
                    length = np.linalg.norm(np.array(end) - np.array(start))
                    area = self.calculate_line_area(length, element_data['profile'])
                    volume = self.calculate_line_volume(length, element_data['profile'])
                    element_data['volume'] = volume
                    element_data['area'] = area

    def calculate_mesh_volume(self, vertices, triangles):
        # Implementa el cálculo del volumen de un mesh
        #...
        pass

    def calculate_mesh_area(self, vertices, triangles):
        # Implementa el cálculo del área de un mesh
        #...
        pass

    def calculate_line_area(self, length, profile):
        # Implementa el cálculo del área de un elemento lineal
        #...
        pass

    def calculate_line_volume(self, length, profile):
        # Implementa el cálculo del volumen de un elemento lineal
        #...
        pass

    def count_properties_by_material(self):
        material_properties = {}
        for element_id, element_data in self.structural_elements.items():
            if 'aterial' in element_data:
                material_name = list(element_data['material'].keys())[0]
                if material_name not in material_properties:
                    material_properties[material_name] = {'volume': 0, 'area': 0}
                material_properties[material_name]['volume'] += element_data.get('volume', 0)
                material_properties[material_name]['area'] += element_data.get('area', 0)
        return material_properties