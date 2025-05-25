# IFCManager

The IFCManager is an open-source Python tool designed to load, analyze, and visualize Architecture, Engineering, and Construction (AEC) models from IFC files. It enables engineers, architects, and researchers to process structural and non-structural elements, extract geometric data, and generate interactive 3D visualizations using Plotly.

## Key Features
- Extracts structural and non-structural elements (beams, columns, slabs, walls, etc.) from IFC files.
- Processes IFC data for AEC model analysis.
- Visualizes AEC models in 3D with Plotly.
- Extensible for custom AEC analysis and visualization workflows.

## Installation
Since this module is not hosted on PyPI, you need to clone the repository and install it locally. Follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/NicoJat/IFCManager.git
   ```

2. Navigate to the project directory:
   ```bash
   cd IFCManager
   ```

3. Install the module and its dependencies:
   ```bash
   pip install -e .
   ```

## Usage
1. Ensure you have an IFC file ready (e.g., place it in `examples/sample_models/`).
2. Open the example notebook:
   - Navigate to `examples/example1.ipynb`.
   - Run the notebook to load, process, and visualize the AEC model.
3. Customize the workflow as needed for your specific analysis or visualization tasks.

## Requirements
- Python 3.7 or higher
- Dependencies: ifcopenshell, plotly, matplotlib, numpy

## Contributing
Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
Nicolás Játiva - [estructurasnj@gmail.com](mailto:estructurasnj@gmail.com)