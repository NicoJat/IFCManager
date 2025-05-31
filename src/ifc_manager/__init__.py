"""
IFC-OpenSeesPy Linker - Convert BIM (IFC) models to structural analysis models for OpenSeesPy.
"""
__version__ = "0.1.0"
__author__ = "Nicolás Játiva"

from .core import IFCManager, IFCParser, ModelVisualizer

# Hacer disponibles las clases principales
__all__ = ['IFCManager', 'IFCParser', 'ModelVisualizer']