import hashlib
import json
from typing import Any


def serialize_projection(projection: Any) -> str:
    """Convierte la proyección semántica en un string determinista."""
    return json.dumps(projection, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def semantic_hash(projection: Any) -> str:
    """Genera el hash SHA-256 de la proyección serializada."""
    serialized = serialize_projection(projection)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
