from dataclasses import dataclass


@dataclass
class VariantSpec:
    gene: str
    mutation: str
