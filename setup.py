from setuptools import setup, find_packages

# Dependencias requeridas
REQUIRED = [
    "numpy>=1.21.0",
    "pandas>=1.3.0",
    "matplotlib>=3.4.0",
    "plotly>=5.0.0",
    "ifcopenshell>=0.7.0"
]

# Dependencias de desarrollo (opcionales)
DEV_REQUIRES = [
    "pytest>=6.2.5",
    "pytest-cov>=2.12.1",
    "black>=21.8b0",
    "flake8>=3.9.2",
    "mypy>=0.910",
]

setup(
    name="ifc-aec-tool",
    version="0.1.0",
    author="Nicolás Játiva",
    author_email="nicolas.jativa12@gmail.com",
    description="Herramienta especializada para la carga, el análisis y la visualización de modelos AEC a partir de archivos IFC",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ifc-aec-tool",
    license="MIT",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ],

    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=REQUIRED,
    extras_require={
        "dev": DEV_REQUIRES,
    },

    entry_points={
        "console_scripts": [
            "ifc-aec-tool=ifc_aec_tool.cli:main",  # Asegúrate de que ifc_aec_tool/cli.py exista y tenga main()
        ],
    },
)