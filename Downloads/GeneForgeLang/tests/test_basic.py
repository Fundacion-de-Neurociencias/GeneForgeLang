import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import sys
import os


# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Pruebas para gene_tokenizer.tokenizer
def test_tokenizer_import():
    """Prueba básica para verificar que el módulo tokenizer se puede importar."""
    try:
        from gene_tokenizer import tokenizer
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo tokenizer"

# Pruebas para gene_tokenizer.utils
def test_utils_import():
    """Prueba básica para verificar que el módulo utils se puede importar."""
    try:
        from gene_tokenizer import utils
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo utils"

# Pruebas para model.config
def test_config_import():
    """Prueba básica para verificar que el módulo config se puede importar."""
    try:
        from model import config
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo config"

# Pruebas para model.gene_transformer
def test_gene_transformer_import():
    """Prueba básica para verificar que el módulo gene_transformer se puede importar."""
    try:
        from model import gene_transformer
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo gene_transformer"

# Pruebas para training.collate_fn
def test_collate_fn_import():
    """Prueba básica para verificar que el módulo collate_fn se puede importar."""
    try:
        from training import collate_fn
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo collate_fn"

# Pruebas para training.dataset_loader
def test_dataset_loader_import():
    """Prueba básica para verificar que el módulo dataset_loader se puede importar."""
    try:
        from training import dataset_loader
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo dataset_loader"

# Pruebas para training.pretrain
def test_pretrain_import():
    """Prueba básica para verificar que el módulo pretrain se puede importar."""
    try:
        from training import pretrain
        assert True
    except ImportError:
        assert False, "No se pudo importar el módulo pretrain"

# Nota: Estas pruebas son básicas y verifican solo la importación de módulos
# ya que los archivos actuales parecen ser marcadores de posición.
# Cuando se implemente el código real, estas pruebas deberán actualizarse
# para probar la funcionalidad específica de cada módulo.
