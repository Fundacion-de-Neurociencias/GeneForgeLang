from typing import Any

from .semantic_hash import semantic_hash
from .semantic_projection import project


def audit_ast(ast_node: Any) -> str:
    projection = project(ast_node)
    return semantic_hash(projection)
