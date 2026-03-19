# src/features/feature_engineering.py
from __future__ import annotations

import pandas as pd


def adicionar_colunas_tempo(df: pd.DataFrame, col_data: str = "data") -> pd.DataFrame:
    """Adiciona ano, mês, dia e dia_da_semana (em português)."""
    df = df.copy()
    df[col_data] = pd.to_datetime(df[col_data])

    df["ano"] = df[col_data].dt.year
    df["mes"] = df[col_data].dt.month
    df["dia"] = df[col_data].dt.day

    dias_semana = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo",
    }
    df["dia_semana"] = df[col_data].dt.dayofweek.map(dias_semana)
    return df


def construir_calendario(inicio: str, fim: str) -> pd.DataFrame:
    """Cria dimensão de datas entre 'inicio' e 'fim', com dia_da_semana em português."""
    datas = pd.date_range(start=inicio, end=fim, freq="D")
    cal = pd.DataFrame({"data": datas})
    cal = adicionar_colunas_tempo(cal, col_data="data")
    return cal
