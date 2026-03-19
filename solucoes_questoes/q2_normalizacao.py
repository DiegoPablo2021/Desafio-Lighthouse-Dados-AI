"""
Q2: Normalização de Produtos

Normaliza e categoriza produtos a partir do arquivo produtos_raw.csv.
- Parte 1: Padroniza categorias para: eletrônicos, propulsão, ancoragem
- Parte 2: Converte preços para tipo numérico
- Parte 3: Remove duplicatas

Premissas obrigatórias:
  - Utiliza apenas o CSV produtos_raw.csv
  - Python 3
"""

import pandas as pd
import re
import sys
from pathlib import Path


def normalizar_categoria(categoria: str) -> str:
    """
    Normaliza variações de grafia nas categorias para os 3 padrões:
      eletrônicos, propulsão, ancoragem.

    Cobre todas as variações encontradas no dataset real, incluindo:
    - Erros de grafia (Propução, Propulçao, Propulssão, Propulsam, etc.)
    - Mixed case (PrOpUlSãO, eLeTrÔnIcOs, aNcOrAgEm)
    - Abreviações (Prop)
    - Versões sem acento (eletronicos, propulsao)
    """
    if pd.isna(categoria):
        return "desconhecida"

    cat = str(categoria).strip().lower()
    # Remover caracteres especiais exceto letras e espaços
    cat = re.sub(r'[^a-záàâãéèêíïóôõöúçñ]', '', cat)

    # Ancoragem
    if any(k in cat for k in ['ancor', 'encor', 'ancoraj']):
        return 'ancoragem'

    # Eletrônicos
    if any(k in cat for k in ['eletr', 'eletron', 'electron']):
        return 'eletrônicos'

    # Propulsão (cobre: propulsão, propulsao, propulssão, propulçao,
    #            propulção, propução, propulsam, prop)
    if any(k in cat for k in ['propul', 'propuç', 'prop']):
        return 'propulsão'

    return cat


def main():
    """Executa normalização de produtos."""

    print("=" * 70)
    print("Q2: NORMALIZAÇÃO DE PRODUTOS")
    print("=" * 70 + "\n")

    # Carregar arquivo
    produtos_file = Path("data/raw/produtos_raw.csv")
    try:
        df = pd.read_csv(produtos_file)
    except Exception as e:
        print(f"Erro ao carregar arquivo: {e}")
        sys.exit(1)

    print(f"Produtos carregados: {len(df)} registros")
    print(f"Colunas: {df.columns.tolist()}\n")

    # Parte 1: Padronizar nomes de categorias
    print("PARTE 1: Normalizando categorias...")
    print(f"  Categorias ANTES (coluna 'actual_category'):")
    for cat in sorted(df['actual_category'].dropna().unique()):
        count = (df['actual_category'] == cat).sum()
        print(f"    [{cat}] x{count}")

    df['actual_category'] = df['actual_category'].apply(normalizar_categoria)

    print(f"\n  Categorias DEPOIS:")
    for cat in sorted(df['actual_category'].unique()):
        count = (df['actual_category'] == cat).sum()
        print(f"    {cat}: {count} produtos")

    # Parte 2: Convertendo valores para tipo numérico
    print("\nPARTE 2: Convertendo valores numéricos...")
    antes_nulos_price = df['price'].isna().sum()
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    depois_nulos_price = df['price'].isna().sum()
    novos_nulos = depois_nulos_price - antes_nulos_price

    print(f"  Preços convertidos com sucesso")
    if novos_nulos > 0:
        print(f"  {novos_nulos} valores não-numéricos convertidos para NaN")
    print(f"  Mínimo: R$ {df['price'].min():,.2f}")
    print(f"  Máximo: R$ {df['price'].max():,.2f}")
    print(f"  Média:  R$ {df['price'].mean():,.2f}")

    # Parte 3: Removendo duplicatas
    print("\nPARTE 3: Removendo duplicatas...")
    duplicatas_antes = len(df)
    df = df.drop_duplicates()
    duplicatas_removidas = duplicatas_antes - len(df)
    print(f"  Duplicatas removidas: {duplicatas_removidas}")
    print(f"  Produtos após limpeza: {len(df)}\n")

    # Salvando o resultado
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "produtos_normalizado.csv"
    df.to_csv(output_file, index=False)
    print(f"Arquivo salvo em: {output_file}")

    print("\n" + "=" * 70)
    print("Q2 concluída com sucesso")
    print("=" * 70)


if __name__ == "__main__":
    main()
