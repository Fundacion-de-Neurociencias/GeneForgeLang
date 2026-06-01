import glob

import pytest

from geneforgelang.utils.grammar_parser import AdvancedGFLParser

parser = AdvancedGFLParser()
files = sorted(glob.glob("bench/corpus/*.gfl"))


@pytest.mark.parametrize("f", files)
def test_parse_corpus(f):
    with open(f, encoding="utf-8").read() as file:
        text = file.read()
    # Si falla el parser, pytest marcará error
    parser.parse(text)
