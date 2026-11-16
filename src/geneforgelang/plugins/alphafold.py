"""Compatibility alias: this module used to hold a copy of ``alpha_genome``.

The copy was a second, diverging implementation of the same stub under a name
that suggests AlphaFold. It now re-exports the single implementation so that
the provenance label and the warning exist in one place.
"""

from geneforgelang.plugins.alpha_genome import AlphaGenomePlugin

__all__ = ["AlphaGenomePlugin"]
