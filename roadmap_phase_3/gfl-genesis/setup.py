from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gfl-genesis",
    version="0.1.0",
    author="GFL Genesis Team",
    author_email="genesis@geneforgelang.org",
    description="GFL Genesis Project: Optimización de ARN Guía (gRNA) para la Edición Genómica de TP53",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fundacion-de-Neurociencias/gfl-genesis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.9",
    install_requires=[
        "geneforgelang>=1.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "biopython>=1.79",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gfl-genesis=main:main",
        ],
    },
)