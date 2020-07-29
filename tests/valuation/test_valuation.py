
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import valuation as v
from valuation import *

def test_checa_dir():
    assert dir(valuation) == 'Modulos'

def test_obtem_wacc():
    expected = 0.1008
    result = v.obtem_wacc(perc_d=0.3, perc_e=0.7, 
                        ke=0.12, kd=0.08, taxa_ir=0.3)
    assert result == pytest.approx(expected), 'WACC incorreto.'


def test_obtem_upside():
    expected = (10/9 - 1, 1)
    result = v.obtem_upside(valor_justo_por_acao=10, cotacao_atual=9)
    assert result == pytest.approx(expected), 'Upside Incorreto.'
