"""
Módulo de Feature Engineering

Funções para criar e transformar variáveis derivadas dos dados brutos,
incluindo agregações temporais e calendário.
"""

from .feature_engineering import adicionar_colunas_tempo, construir_calendario

__all__ = [
    "adicionar_colunas_tempo",
    "construir_calendario",
]
