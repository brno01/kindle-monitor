"""Coloca server/ no sys.path (o modo -I do Python nao inclui o diretorio atual)."""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

# termo ficticio usado nos testes do filtro de privacidade (termos_bloqueados)
TERMO_BLOQUEADO = "empresa-x"
