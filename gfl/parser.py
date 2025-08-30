import hashlib
import logging
from typing import Any, Dict, Optional

import yaml

from .performance import cached, get_monitor

logger = logging.getLogger(__name__)


@cached(cache_name="ast_parse", ttl=300.0, max_size=100)
def parse_gfl(gfl_string: str) -> Optional[Dict[str, Any]]:
    """
    Parses a GFL string (in YAML format) into a Python dictionary.

    This function is cached for performance - identical GFL strings
    will return cached results for up to 5 minutes.

    Args:
        gfl_string: The GFL source code as a string.

    Returns:
        Parsed AST as a dictionary, or None if parsing fails.
    """
    with get_monitor().time_operation("gfl_parse"):
        try:
            # Hash the input for cache key generation
            input_hash = hashlib.sha256(gfl_string.encode()).hexdigest()[:16]
            logger.debug(f"Parsing GFL content (hash: {input_hash})")

            data = yaml.safe_load(gfl_string)

            if data is None:
                logger.warning("GFL parsing resulted in None (empty document?)")

            return data

        except yaml.YAMLError as e:
            logger.error(f"Error parsing GFL YAML: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during GFL parsing: {e}")
            return None
