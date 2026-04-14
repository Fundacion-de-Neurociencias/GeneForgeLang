import sys
import logging

from geneforgelang.core import parse_gfl, validate, execute

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
        ast = parse_gfl(gfl_code)
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

        # Execution
        execution_result = execute(ast)
        if not execution_result:
            logger.error("Execution failed to produce results.")
            return
        logger.info("GFL script execution complete.")
        #print(execution_result)

    except Exception as e:
        logger.exception(f"An unexpected error occurred during GFL processing: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <gfl_file_path>")
        sys.exit(1)

    gfl_file = sys.argv[1]
    main(gfl_file)
