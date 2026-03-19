# src/models/forecasting.py
from __future__ import annotations

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error


def filtrar_produto(df: pd.DataFrame, id_produto: int) -> pd.DataFrame:
    """Filtra um produto pelo ID e retorna o DataFrame filtrado."""
    # Detectar nomes de colunas variáveis
    col_product = 'id_product' if 'id_product' in df.columns else 'produto'
    col_date = 'sale_date' if 'sale_date' in df.columns else 'data'
    col_total = 'total' if 'total' in df.columns else 'qtd_vendida'
    
    # Filtrar produto e garantir que data seja datetime
    df_filtrado = df[df[col_product] == id_produto].copy()
    df_filtrado[col_date] = pd.to_datetime(df_filtrado[col_date])
    
    return df_filtrado


def baseline_media_movel_7_dias(serie: pd.Series) -> pd.Series:
    """Retorna previsão com média móvel dos últimos 7 dias (shift + rolling)."""
    return serie.shift(1).rolling(window=7, min_periods=1).mean()


def treinar_e_prever_baseline(
    df_vendas: pd.DataFrame,
    data_treino_fim: str,
    data_teste_inicio: str,
    data_teste_fim: str,
) -> tuple[pd.DataFrame, float]:
    """
    Aplica baseline de média móvel 7 dias e calcula MAE no período de teste.
    df_vendas deve ter colunas: 'data' e 'vendas'.
    """
    df = df_vendas.copy()
    df["data"] = pd.to_datetime(df["data"])
    df = df.sort_values("data")

    df["y"] = df["vendas"]
    df["y_pred"] = baseline_media_movel_7_dias(df["y"])

    treino_mask = df["data"] <= pd.to_datetime(data_treino_fim)
    teste_mask = (df["data"] >= pd.to_datetime(data_teste_inicio)) & (
        df["data"] <= pd.to_datetime(data_teste_fim)
    )

    df_teste = df.loc[teste_mask, ["data", "y", "y_pred"]].dropna()
    mae = mean_absolute_error(df_teste["y"], df_teste["y_pred"]) if not df_teste.empty else np.nan

    return df, mae
