import glob

import pytest

from geneforgelang.utils.grammar_parser import AdvancedGFLParser

parser = AdvancedGFLParser()
files = sorted(glob.glob("tests\\bench\\corpus\\*.gfl"))
print(files)


@pytest.mark.parametrize("file", files)
def test_parse_corpus(file):
    with open(file, encoding="utf-8") as f:
        text = f.read()
    # Si falla el parser, pytest marcará error
    parser.parse(text)
