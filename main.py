import os
import sys

# Add the project root to the Python path
# This helps resolve imports like 'gfl.parser', 'gfl.plugins', etc., correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging

from gfl import parser
from gfl.interpreter import Interpreter
from gfl.semantic_validator import validate

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more verbose output
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main(gfl_file_path):
    logger.info(f"Starting GFL interpreter for: {gfl_file_path}")

    with open(gfl_file_path) as f:
        gfl_code = f.read()

    try:
        # Lexing and Parsing
        ast = parser.parse(gfl_code)
        if not ast:
            logger.error("Failed to parse GFL code.")
            return

        # Semantic Validation
        errors = validate(ast)
        if errors:
            logger.error("Semantic validation errors found:")
            for error in errors:
                logger.error(f"- {error}")
            return
        logger.info("Semantic validation successful.")

        # Interpretation
        interpreter = Interpreter()
        interpreter.interpret(ast)
        logger.info("GFL script execution complete.")

    except Exception as e:
        logger.exception(f"An unexpected error occurred during GFL processing: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <gfl_file_path>")
        sys.exit(1)

    gfl_file = sys.argv[1]
    main(gfl_file)
