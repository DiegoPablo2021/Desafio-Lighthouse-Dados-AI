# src/models/recommendation.py
from __future__ import annotations

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def construir_matriz_usuario_item(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói matriz usuário × item (0/1) com base em df contendo
    colunas de cliente e produto.
    """
    # Detectar nomes de colunas variáveis
    col_cliente = 'id_client' if 'id_client' in df.columns else 'id_cliente'
    col_produto = 'id_product' if 'id_product' in df.columns else 'id_produto'
    
    matriz = (
        df.assign(valor=1)
        .drop_duplicates(subset=[col_cliente, col_produto])
        .pivot_table(
            index=col_cliente,
            columns=col_produto,
            values="valor",
            fill_value=0,
            aggfunc="max",
        )
    )
    return matriz


def calcular_similaridade_produtos(matriz_ui: pd.DataFrame) -> pd.DataFrame:
    """Retorna matriz de similaridade produto × produto (cosine)."""
    produtos = matriz_ui.columns
    sim = cosine_similarity(matriz_ui.T)
    sim_df = pd.DataFrame(sim, index=produtos, columns=produtos)
    return sim_df


def top_k_similares(sim_df: pd.DataFrame, id_produto_ref: int, k: int = 5) -> pd.Series:
    """
    Retorna série com os k produtos mais similares ao produto de referência,
    excluindo o próprio.
    """
    similares = sim_df.loc[id_produto_ref].drop(labels=[id_produto_ref])
    return similares.sort_values(ascending=False).head(k)
