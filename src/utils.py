# src/utils.py
from pathlib import Path
import pandas as pd


def garantir_pasta(path: str | Path) -> None:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)


def salvar_csv(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    garantir_pasta(path.parent)
    df.to_csv(path, index=False)
    print(f"Arquivo salvo em: {path}")