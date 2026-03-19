"""
Módulo de Modelagem

Funções para construir modelos de previsão e sistema de recomendação,
incluindo baseline, ajustes de hyperparâmetros e avaliação.
"""

from .forecasting import (
    filtrar_produto,
    baseline_media_movel_7_dias,
    treinar_e_prever_baseline,
)
from .recommendation import (
    construir_matriz_usuario_item,
    calcular_similaridade_produtos,
    top_k_similares,
)

__all__ = [
    "filtrar_produto",
    "baseline_media_movel_7_dias",
    "treinar_e_prever_baseline",
    "construir_matriz_usuario_item",
    "calcular_similaridade_produtos",
    "top_k_similares",
]
