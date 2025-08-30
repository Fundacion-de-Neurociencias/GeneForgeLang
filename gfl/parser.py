import logging

import yaml

logger = logging.getLogger(__name__)


def parse_gfl(gfl_string):
    """
    Parses a GFL string (in YAML format) into a Python dictionary.
    """
    try:
        data = yaml.safe_load(gfl_string)
        return data
    except yaml.YAMLError as e:
        logger.error(f"Error parsing GFL YAML: {e}")
        return None
