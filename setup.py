from setuptools import setup, find_packages

# Dependencias de desarrollo (opcionales)
DEV_REQUIRES = [
    "pytest>=6.2.5",
    "pytest-cov>=2.12.1",
    "black>=21.8b0",
    "flake8>=3.9.2",
    "mypy>=0.910",
]

setup(
    # Metadatos básicos (tuyos y del proyecto)
    name="ifc-openseespy-linker",
    version="0.1.0",
    author="Nicolás Játiva",
    author_email="nicolas.jativa12@gmail.com",
    description="Convierte modelos BIM (IFC) a modelos de análisis estructural para OpenSeesPy",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/ifc-openseespy-linker",
    license="MIT",
    
    # Clasificadores (opciones en: https://pypi.org/classifiers/)
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    
    # Estructura del paquete
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    
    # Dependencias
    extras_require={
        "dev": DEV_REQUIRES,
        # Puedes añadir más grupos: docs, test, etc.
    },
    
    # Opcional: Scripts de consola
    entry_points={
        "console_scripts": [
            "ifc2opensees=ifc_openseespy_linker.cli:main",
        ],
    },
)