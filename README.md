# IFC-OpenSeesPy Linker

A Python library to seamlessly convert IFC structural models to OpenSeesPy for advanced structural analysis.

## Quick Start

```python
from ifc_openseespy_linker import IFCConverter

# Initialize converter with IFC file
converter = IFCConverter("path/to/model.ifc")

# Extract structural elements
converter.extract_elements()

# Create OpenSeesPy model
opensees_model = converter.create_opensees_model()

# Run analysis
results = opensees_model.analyze()

# Visualize results
converter.visualize_results(results)