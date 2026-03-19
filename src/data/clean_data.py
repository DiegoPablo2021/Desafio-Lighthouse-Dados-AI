# data/clean_data.py
import re
from typing import Any, Optional
import pandas as pd


def normalizar_categoria(cat: Any) -> Optional[str]:
    """Normaliza categorias para: eletronicos, propulsao, ancoragem."""
    if pd.isna(cat):
        return None
    cat_str = re.sub(r"\s+", "", str(cat).strip().lower())

    if any(x in cat_str for x in ["eletr", "eletro", "eltro"]):
        return "eletronicos"
    if any(x in cat_str for x in ["propul", "propls", "prop"]):
        return "propulsao"
    if any(x in cat_str for x in ["ancor", "encor", "ancora"]):
        return "ancoragem"
    return cat_str


def limpar_preco(valor: Any) -> Optional[float]:
    """Converte string de preço para float, retornando None em caso de erro."""
    if pd.isna(valor):
        return None
    valor_str = re.sub(r"[R\$\s]", "", str(valor)).replace(",", ".")
    try:
        return float(valor_str)
    except ValueError:
        return None


def clean_produtos(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica normalização de categorias, conversão numérica e remoção de duplicatas."""
    if "actual_category" in df.columns and "actualcategory" not in df.columns:
        df = df.rename(columns={"actual_category": "actualcategory"})

    df["actualcategory"] = df["actualcategory"].apply(normalizar_categoria)

    df["price"] = df["price"].apply(limpar_preco)
    df["code"] = pd.to_numeric(df["code"], errors="coerce")

    qtd_antes = len(df)
    df = df.drop_duplicates(subset=["code"], keep="first")
    qtd_depois = len(df)

    print(f"Duplicatas removidas    : {qtd_antes - qtd_depois}")
    print(f"Total de produtos únicos: {qtd_depois}")
    print(f"Categorias finais       : {sorted(df['actualcategory'].dropna().unique())}")
    return df
