from setuptools import find_packages, setup

setup(
    name="gfl-plugin-ontarget-scorer",
    version="0.1.0",
    description="GFL Plugin for predicting CRISPR-Cas9 on-target cutting efficiency",
    author="GFL Genesis Team",
    packages=find_packages(),
    install_requires=[
        "geneforgelang>=1.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "biopython>=1.79",
    ],
    entry_points={"gfl.plugins": ["ontarget_scorer = gfl_plugin_ontarget_scorer.plugin:OnTargetScorerPlugin"]},
    python_requires=">=3.9",
)
