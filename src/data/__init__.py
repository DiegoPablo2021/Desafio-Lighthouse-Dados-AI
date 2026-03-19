"""
Módulo de Carregamento de Dados

Funções para carregar arquivos de dados brutos em diferentes formatos
(CSV, JSON) com validação e padronização automática.
"""

from .load_data import load_vendas, load_produtos, load_clientes, load_custos
from .clean_data import normalizar_categoria, limpar_preco, clean_produtos

__all__ = [
    "load_vendas",
    "load_produtos", 
    "load_clientes",
    "load_custos",
    "normalizar_categoria",
    "limpar_preco",
    "clean_produtos",
]
