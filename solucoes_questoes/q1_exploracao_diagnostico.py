"""
Q1: Exploracao e Diagnostico dos Dados de Vendas (2023-2024)

Premissas obrigatorias:
  - Utiliza APENAS o dataset vendas_2023_2024.csv
  - NAO faz limpeza nem tratamento dos dados
  - Apenas observa, agrega e descreve

Entregas:
  - Parte 1: Qtd linhas, qtd colunas, intervalo de datas
  - Parte 2: Valor min, max e medio da coluna "total"
  - Parte 3 (Q1.3): Diagnostico de confiabilidade
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).parent.parent


def main():
    print("\n" + "=" * 70)
    print("Q1: EXPLORACAO E DIAGNOSTICO DOS DADOS")
    print("=" * 70 + "\n")

    # ---------------------------------------------------------------
    # Carregar dataset (APENAS vendas_2023_2024.csv)
    # ---------------------------------------------------------------
    vendas_path = ROOT_DIR / "data" / "raw" / "vendas_2023_2024.csv"
    try:
        df = pd.read_csv(vendas_path)
    except Exception as e:
        print(f"ERRO: Falha ao carregar {vendas_path}: {e}")
        sys.exit(1)

    # Converter coluna de data (sem eliminar registros)
    df['sale_date'] = pd.to_datetime(df['sale_date'], format='mixed', dayfirst=True)

    # ---------------------------------------------------------------
    # PARTE 1 - Visao geral do dataset
    # ---------------------------------------------------------------
    print("PARTE 1 - VISAO GERAL DO DATASET:")
    print(f"  Quantidade total de linhas:  {df.shape[0]:,}")
    print(f"  Quantidade total de colunas: {df.shape[1]}")
    print(f"  Data minima: {df['sale_date'].min().date()}")
    print(f"  Data maxima: {df['sale_date'].max().date()}")
    print()

    # ---------------------------------------------------------------
    # PARTE 2 - Analise de valores numericos (coluna "total")
    # ---------------------------------------------------------------
    print("PARTE 2 - ANALISE DE VALORES NUMERICOS (coluna 'total'):")
    print(f"  Valor minimo: R$ {df['total'].min():,.2f}")
    print(f"  Valor maximo: R$ {df['total'].max():,.2f}")
    print(f"  Valor medio:  R$ {df['total'].mean():,.2f}")
    print()

    # Estatisticas complementares
    print("  Estatisticas complementares:")
    print(f"    Mediana:       R$ {df['total'].median():,.2f}")
    print(f"    Desvio padrao: R$ {df['total'].std():,.2f}")
    print(f"    Clientes unicos:  {df['id_client'].nunique()}")
    print(f"    Produtos unicos:  {df['id_product'].nunique()}")
    print()

    # ---------------------------------------------------------------
    # PARTE 3 - Q1.3: Diagnostico de confiabilidade
    # ---------------------------------------------------------------
    print("=" * 70)
    print("Q1.3 - DIAGNOSTICO DE CONFIABILIDADE DO DATASET")
    print("=" * 70)

    total_nulos = df.isnull().sum().sum()
    total_negativos = (df['total'] < 0).sum()
    q1 = df['total'].quantile(0.25)
    q3 = df['total'].quantile(0.75)
    iqr = q3 - q1
    outliers_sup = int((df['total'] > q3 + 1.5 * iqr).sum())
    outliers_inf = int((df['total'] < q1 - 1.5 * iqr).sum())

    print()
    print("1. OUTLIERS na coluna 'total':")
    print(f"   Q1 = R$ {q1:,.2f} | Q3 = R$ {q3:,.2f} | IQR = R$ {iqr:,.2f}")
    print(f"   Outliers superiores (> Q3 + 1.5*IQR): {outliers_sup}")
    print(f"   Outliers inferiores (< Q1 - 1.5*IQR): {outliers_inf}")
    if outliers_sup > 0:
        pct = outliers_sup / len(df) * 100
        print(f"   -> Existem {outliers_sup} transacoes ({pct:.1f}%) com valores")
        print(f"      atipicamente altos, possivelmente vendas em grande volume.")
    else:
        print("   -> Nao foram detectados outliers significativos.")

    print()
    print("2. QUALIDADE DOS DADOS:")
    print(f"   Valores nulos no dataset:         {total_nulos}")
    print(f"   Valores negativos em 'total':      {total_negativos}")
    if total_nulos == 0 and total_negativos == 0:
        print("   -> O dataset NAO apresenta valores faltantes nem negativos.")
        print("      Boa integridade geral dos registros.")
    else:
        if total_nulos > 0:
            print(f"   -> Ha {total_nulos} valores nulos que precisam de tratamento.")
        if total_negativos > 0:
            print(f"   -> Ha {total_negativos} valores negativos (possiveis estornos).")

    print()
    print("3. CONCLUSAO - O dataset esta pronto para analises?")
    if total_nulos == 0 and total_negativos == 0 and outliers_sup < len(df) * 0.05:
        print("   SIM. O dataset vendas_2023_2024.csv apresenta boa qualidade geral:")
        print(f"   - {df.shape[0]:,} registros sem valores nulos")
        print("   - Sem valores negativos em 'total'")
        print(f"   - Outliers representam apenas {outliers_sup / len(df) * 100:.1f}%")
        print("     dos registros, dentro de margem aceitavel")
        print("   - Recomendacao: pode ser utilizado diretamente para analises,")
        print("     com atencao a possiveis outliers em resultados agregados.")
    else:
        print("   PARCIALMENTE. O dataset exige tratamento previo antes de")
        print("   analises confiaveis. Recomenda-se tratar os pontos acima.")

    print("\n" + "=" * 70)
    print("Q1 concluida com sucesso")
    print("=" * 70)


if __name__ == "__main__":
    main()
