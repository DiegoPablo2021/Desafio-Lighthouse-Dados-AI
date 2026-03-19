"""
Q6: Dimensão Calendário e Análise de Sazonalidade

Constrói uma dimensão de datas (calendário completo) e cruza com
a tabela de vendas para calcular a média REAL de vendas por dia
da semana, incluindo dias SEM vendas (= R$ 0).

Premissas obrigatórias:
  - Período: todas as datas entre MIN(sale_date) e MAX(sale_date)
  - A loja esteve aberta TODOS os dias (inclusive fins de semana)
  - Dias sem registro = valor_venda = R$ 0
  - "Vendas diárias" = SUM(total) por dia
  - Média por dia da semana = considerando TODOS os dias do calendário
  - Dia da semana em português (Segunda-feira, Terça-feira, etc.)
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta


# Mapeamento do dia da semana (0=Monday no Python)
DIAS_SEMANA = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}


def main():
    """Executa criação de dimensão calendário com análise de sazonalidade."""

    print("=" * 70)
    print("Q6: DIMENSÃO CALENDÁRIO COM SAZONALIDADE")
    print("=" * 70 + "\n")

    # 1. Carregar vendas
    print("1. Carregando dados de vendas...")
    df_vendas = pd.read_csv('data/raw/vendas_2023_2024.csv')
    df_vendas['sale_date'] = pd.to_datetime(df_vendas['sale_date'], format='mixed')

    data_min = df_vendas['sale_date'].min()
    data_max = df_vendas['sale_date'].max()
    print(f"   Total de registros: {len(df_vendas)}")
    print(f"   Período: {data_min.date()} a {data_max.date()}\n")

    # 2. Agregar vendas por data
    print("2. Agregando vendas por data...")
    vendas_por_dia = df_vendas.groupby(df_vendas['sale_date'].dt.date).agg(
        valor_venda=('total', 'sum'),
        num_transacoes=('id', 'count')
    ).reset_index()
    vendas_por_dia.columns = ['data', 'valor_venda', 'num_transacoes']
    vendas_por_dia['data'] = pd.to_datetime(vendas_por_dia['data'])

    dias_com_venda = len(vendas_por_dia)
    print(f"   Dias com pelo menos 1 venda: {dias_com_venda}\n")

    # 3. Gerar CALENDÁRIO COMPLETO (todas as datas do período)
    print("3. Gerando calendário completo...")
    calendario = pd.date_range(start=data_min.date(), end=data_max.date(), freq='D')
    df_calendario = pd.DataFrame({'data': calendario})

    total_dias = len(df_calendario)
    print(f"   Total de dias no calendário: {total_dias}")
    print(f"   Dias SEM venda (serão zero): {total_dias - dias_com_venda}\n")

    # 4. LEFT JOIN: calendário ← vendas (dias sem venda ficam com 0)
    print("4. Cruzando calendário com vendas (LEFT JOIN)...")
    df_completo = df_calendario.merge(vendas_por_dia, on='data', how='left')
    df_completo['valor_venda'] = df_completo['valor_venda'].fillna(0)
    df_completo['num_transacoes'] = df_completo['num_transacoes'].fillna(0).astype(int)

    # Adicionar colunas de calendário
    df_completo['dia_semana'] = df_completo['data'].dt.dayofweek.map(DIAS_SEMANA)
    df_completo['dia_semana_num'] = df_completo['data'].dt.dayofweek
    df_completo['dia_mes'] = df_completo['data'].dt.day
    df_completo['mes'] = df_completo['data'].dt.month
    df_completo['ano'] = df_completo['data'].dt.year
    df_completo['trimestre'] = df_completo['data'].dt.quarter
    df_completo['semana_ano'] = df_completo['data'].dt.isocalendar().week.astype(int)
    df_completo['eh_fim_semana'] = (df_completo['dia_semana_num'] >= 5).astype(int)

    print(f"   Registros no calendário completo: {len(df_completo)}")
    print(f"   Verificação — dias com valor_venda = 0: {(df_completo['valor_venda'] == 0).sum()}\n")

    # 5. Calcular MÉDIA de vendas por dia da semana (incluindo zeros!)
    print("5. Calculando média de vendas por dia da semana...\n")

    media_por_dia = df_completo.groupby(['dia_semana_num', 'dia_semana']).agg(
        total_dias=('data', 'count'),
        dias_com_venda=('num_transacoes', lambda x: (x > 0).sum()),
        soma_vendas=('valor_venda', 'sum'),
        media_vendas=('valor_venda', 'mean')
    ).reset_index().sort_values('dia_semana_num')

    print("RESULTADO — Média de Vendas por Dia da Semana:")
    print("-" * 85)
    print(f"{'Dia da Semana':<18} {'Total Dias':<12} {'Dias c/ Venda':<15} {'Total (R$)':<18} {'Média (R$)':<15}")
    print("-" * 85)

    for _, row in media_por_dia.iterrows():
        print(
            f"{row['dia_semana']:<18} "
            f"{int(row['total_dias']):<12} "
            f"{int(row['dias_com_venda']):<15} "
            f"R$ {row['soma_vendas']:>14,.2f} "
            f"R$ {row['media_vendas']:>12,.2f}"
        )

    print("-" * 85)

    # Q6.2 — Validação: qual dia da semana tem a MENOR média?
    pior_dia = media_por_dia.loc[media_por_dia['media_vendas'].idxmin()]
    print(f"\nQ6.2 — VALIDAÇÃO:")
    print(f"   Dia com MENOR média de vendas: {pior_dia['dia_semana']}")
    print(f"   Média: R$ {pior_dia['media_vendas']:,.2f}")

    # Q6.3 — Explicação
    print(f"\nQ6.3 — EXPLICAÇÃO:")
    print("-" * 70)
    print("  Por que é necessário utilizar uma tabela de datas (calendário)?")
    print()
    print("  Se agruparmos diretamente a tabela de vendas por dia da semana,")
    print("  dias em que a loja ABRIU mas vendeu zero NÃO existem na tabela.")
    print("  Esses dias são ignorados, inflando a média artificialmente.")
    print()
    print("  Exemplo: se em 52 terças-feiras do ano a loja vendeu em apenas 30,")
    print("  agrupar diretamente calcularia a média apenas sobre 30 dias,")
    print("  quando o correto seria sobre 52 dias (incluindo 22 dias com R$ 0).")
    print()
    print("  O que aconteceria com a média se muitos dias não tivessem venda?")
    print("  A média seria INFLADA. Ex: total de R$ 150.000 ÷ 30 dias = R$ 5.000,")
    print("  quando na verdade deveria ser R$ 150.000 ÷ 52 dias = R$ 2.884,62.")
    print("  Isso levaria a decisões erradas (como achar que terça é um bom dia).")

    # 6. Salvar resultado
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "dim_calendario.csv"
    df_output = df_completo[['data', 'dia_mes', 'mes', 'ano', 'trimestre',
                              'semana_ano', 'dia_semana', 'dia_semana_num',
                              'eh_fim_semana', 'num_transacoes', 'valor_venda']]
    df_output.to_csv(output_file, index=False)
    print(f"\nDimensão calendário salva em: {output_file}")

    print("\n" + "=" * 70)
    print("Q6 concluída com sucesso")
    print("=" * 70)


if __name__ == "__main__":
    main()
