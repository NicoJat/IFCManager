# src/ifc_openseespy_linker/__init__.py
"""
IFC-OpenSeesPy Linker - Convert BIM (IFC) models to structural analysis models for OpenSeesPy.
"""
__version__ = "0.1.0"
__author__ = "Nicolás Játiva"

from .core.ifc_parser import IFCParser
from .core.opensees_converter import OpenSeesConverter
from .core.visualization import ModelVisualizer