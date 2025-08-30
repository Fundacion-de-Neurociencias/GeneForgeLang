import sys
import argparse
from gfl.api import parse, validate


def cmd_parse():
    ap = argparse.ArgumentParser(
        description="Parse GFL (YAML) to AST and print it."
    )
    ap.add_argument("file", help="Path to GFL YAML file")
    args = ap.parse_args()
    text = open(args.file, encoding="utf-8").read()
    ast = parse(text)
    print(ast)


def cmd_validate():
    ap = argparse.ArgumentParser(
        description="Validate GFL (YAML) semantics."
    )
    ap.add_argument("file", help="Path to GFL YAML file")
    args = ap.parse_args()
    text = open(args.file, encoding="utf-8").read()
    ast = parse(text)
    errs = validate(ast)
    if errs:
        for e in errs:
            print(f"- {e}")
        sys.exit(1)
    print("OK")
