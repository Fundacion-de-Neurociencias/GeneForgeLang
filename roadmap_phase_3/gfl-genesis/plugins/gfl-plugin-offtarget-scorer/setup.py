from setuptools import setup, find_packages

setup(
    name="gfl-plugin-offtarget-scorer",
    version="0.1.0",
    description="GFL Plugin for identifying and scoring CRISPR-Cas9 off-target sites",
    author="GFL Genesis Team",
    packages=find_packages(),
    install_requires=[
        "geneforgelang>=1.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "biopython>=1.79",
    ],
    entry_points={
        "gfl.plugins": [
            "offtarget_scorer = gfl_plugin_offtarget_scorer.plugin:OffTargetScorerPlugin"
        ]
    },
    python_requires=">=3.9",
)