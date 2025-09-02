from setuptools import setup, find_packages

setup(
    name="gfl-crispr-evaluator",
    version="0.1.0",
    description="GFL Plugin for orchestrating CRISPR gRNA evaluation",
    author="GFL Genesis Team",
    packages=find_packages(),
    install_requires=[
        "geneforgelang>=1.0.0",
        "gfl-plugin-ontarget-scorer>=0.1.0",
        "gfl-plugin-offtarget-scorer>=0.1.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
    ],
    entry_points={
        "gfl.plugins": [
            "crispr_evaluator = gfl_crispr_evaluator.plugin:CRISPREvaluatorPlugin"
        ]
    },
    python_requires=">=3.9",
)
