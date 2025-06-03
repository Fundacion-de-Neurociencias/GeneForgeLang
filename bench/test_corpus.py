import glob
import pytest
from gfl.parser import GFLParser, GFLParseError

parser = GFLParser()
files = sorted(glob.glob("bench/corpus/*.gfl"))

@pytest.mark.parametrize("f", files)
def test_parse_corpus(f):
    text = open(f, encoding="utf-8").read()
    # Si falla el parser, pytest marcará error
    parser.parse(text)
