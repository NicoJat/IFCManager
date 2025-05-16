# IFC-OpenSeesPy Linker

The IFC-OpenSeesPy Linker is an open-source Python tool designed to convert Building Information Modeling (BIM) data from IFC files into structural analysis models for OpenSeesPy. It enables engineers and researchers to seamlessly transition from BIM to finite element analysis by extracting structural elements, processing geometry, and generating OpenSeesPy inputs. The tool includes 3D visualization capabilities using Plotly.

## Key Features
- Extracts structural elements (beams, columns, slabs, etc.) from IFC files.
- Converts IFC data into OpenSeesPy-compatible structural models.
- Visualizes structural models in 3D with Plotly.
- Extensible for custom analysis workflows.

## Installation
```bash
pip install -e .
```

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ifc-openseespy-linker.git
   ```
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Run the example notebook:
   - Open `examples/example1.ipynb`.
   - Ensure an IFC file is in `examples/sample_models/`.
   - Execute the notebook to load, process, and visualize the model.

## Requirements
- Python 3.7 or higher
- Dependencies: `ifcopenshell`, `openseespy`, `plotly`, `matplotlib`, `numpy`

## Contributing
Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
Nicolás Játiva - [nicolas.jativa12@gmail.com](mailto:nicolas.jativa12@gmail.com)
