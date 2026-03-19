# data/load_data.py
from pathlib import Path
import pandas as pd
import os

# Compatível com notebooks e scripts
try:
    BASE_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
except (NameError, RuntimeError):
    # Em notebooks Jupyter, __file__ não está definido
    BASE_RAW = Path(os.getcwd()).parent / "data" / "raw"


def load_vendas(path: str | Path = BASE_RAW / "vendas_2023_2024.csv") -> pd.DataFrame:
    """Carrega o arquivo de vendas e padroniza tipos."""
    df = pd.read_csv(path)

    print(f"Colunas encontradas em vendas: {df.columns.tolist()}")

    # Detecta coluna de data
    colunas_data = [
        c for c in df.columns
        if any(k in c.lower() for k in ["data", "date", "dt"])
    ]
    if colunas_data:
        col_data = colunas_data[0]
        print(f"Coluna de data detectada: '{col_data}'")
        # Usa format='mixed' para lidar com formatos mistos
        df[col_data] = pd.to_datetime(df[col_data], format='mixed', dayfirst=True)
    else:
        print("AVISO: Nenhuma coluna de data encontrada automaticamente.")

    # Detecta coluna de total
    colunas_total = [
        c for c in df.columns
        if any(k in c.lower() for k in ["total", "valor", "preco", "preço"])
    ]
    if colunas_total:
        col_total = colunas_total[0]
        print(f"Coluna de total detectada: '{col_total}'")

    print(f"Shape final de vendas: {df.shape}")

    # Renomeia sale_date -> data para compatibilidade com notebooks
    if "sale_date" in df.columns:
        df = df.rename(columns={"sale_date": "data"})

    return df


def load_produtos(path: str | Path = BASE_RAW / "produtos_raw.csv") -> pd.DataFrame:
    """Carrega o arquivo produtos_raw.csv."""
    df = pd.read_csv(path)
    print(f"Colunas encontradas em produtos: {df.columns.tolist()}")
    print(f"Shape de produtos: {df.shape}")
    return df


def load_clientes(path: str | Path = BASE_RAW / "clientes_crm.json") -> pd.DataFrame:
    """Carrega o arquivo clientes_crm.json."""
    df = pd.read_json(path)
    print(f"Colunas encontradas em clientes: {df.columns.tolist()}")
    print(f"Shape de clientes: {df.shape}")
    return df


def load_custos(path: str | Path = BASE_RAW / "custos_importacao.json") -> pd.DataFrame:
    """Carrega o arquivo custos_importacao.json."""
    df = pd.read_json(path)
    print(f"Colunas encontradas em custos: {df.columns.tolist()}")
    print(f"Shape de custos: {df.shape}")
    return df
