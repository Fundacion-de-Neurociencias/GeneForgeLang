import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

# Pruebas para gene_tokenizer.tokenizer
def test_tokenizer_import():
    try:
        from gene_tokenizer import tokenizer
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo tokenizer"

# Pruebas para gene_tokenizer.utils
def test_utils_import():
    try:
        from gene_tokenizer import utils
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo utils"

# Pruebas para model.config
def test_config_import():
    try:
        from model import config
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo config"

# Pruebas para model.gene_transformer
def test_gene_transformer_import():
    try:
        from model import gene_transformer
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo gene_transformer"

# Pruebas para training.collate_fn
def test_collate_fn_import():
    try:
        from training import collate_fn
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo collate_fn"

# Pruebas para training.dataset_loader
def test_dataset_loader_import():
    try:
        from training import dataset_loader
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo dataset_loader"

# Pruebas para training.pretrain
def test_pretrain_import():
    try:
        from training import pretrain
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo pretrain"

# Pruebas específicas para nuevas construcciones simbólicas de GFL
from parser import parse_geneforge_line

def test_rna_transport():
    line = "EDIT:RNA_Transport(NRXN1→neurite_tip){method=CRISPR-TO}"
    result = parse_geneforge_line(line)
    assert result["valid"]
    assert result["rna_transport"] == [{"from": "NRXN1", "to": "neurite_tip", "metadata": "method=CRISPR-TO"}]

def test_effect():
    line = "EFFECT(↑neurite_growth@24h){magnitude=50%}"
    result = parse_geneforge_line(line)
    assert result["valid"]
    assert result["effects"][0]["direction"] == "↑"
    assert result["effects"][0]["effect"] == "neurite_growth"
    assert result["effects"][0]["time"] == "24h"
    assert result["effects"][0]["metadata"] == "magnitude=50%"

def test_localized():
    line = "localized(RNA=NRXN1)"
    result = parse_geneforge_line(line)
    assert result["valid"]
    assert result["localized"] == ["NRXN1"]

def test_hypothesis():
    line = "HYPOTHESIS: if localized(RNA=NRXN1) then repair(synapse)"
    result = parse_geneforge_line(line)
    assert result["valid"]
    assert result["hypotheses"] == [{"if": "localized(RNA=NRXN1)", "then": "repair(synapse)"}]

def test_simulate():
    line = "SIMULATE: {EDIT:RNA_Transport(...), OUTCOME=Regrowth(neurite)}"
    result = parse_geneforge_line(line)
    assert result["valid"]
    assert "EDIT:RNA_Transport(...), OUTCOME=Regrowth(neurite)" in result["simulations"]
