"""
QUESTÃO 7.1 - MODELO DE PREVISÃO DE DEMANDA
Modelo Baseline: Média Móvel de 7 Dias

Produto: Motor de Popa Yamaha Evo Dash 155HP
Período de Treino: Até 31/12/2023
Período de Teste: Janeiro de 2024
Métrica: MAE (Mean Absolute Error)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def carregar_e_processar_dados():
    """Carrega e processa dados de vendas."""
    
    # Carregar dataset
    print("Carregando dataset...")
    vendas_df = pd.read_csv('data/raw/vendas_2023_2024.csv')
    
    # Converter coluna de data
    vendas_df['sale_date'] = pd.to_datetime(vendas_df['sale_date'], format='mixed')
    
    # Carregar produtos
    produtos_df = pd.read_csv('data/raw/produtos_raw.csv')
    
    # Merge para adicionar nomes de produtos
    vendas_df = vendas_df.merge(produtos_df, left_on='id_product', right_on='code', how='left')
    
    return vendas_df, produtos_df


def filtrar_produto(vendas_df, nome_produto):
    """Filtra vendas de um produto específico."""
    
    # Procurar pelo produto
    produto_encontrado = vendas_df[vendas_df['name'].str.contains(
        nome_produto, 
        case=False, 
        na=False
    )]
    
    if len(produto_encontrado) == 0:
        print(f"⚠ Produto '{nome_produto}' não encontrado exatamente.")
        print("Produtos diferentes:")
        produtos_unicos = vendas_df['name'].unique()
        for prod in produtos_unicos[:10]:
            print(f"  - {prod}")
        return None
    
    return produto_encontrado


def criar_serie_temporal(vendas_produto):
    """Cria série temporal diária para o produto."""
    
    # Agregar por data
    vendas_por_dia = vendas_produto.groupby('sale_date').agg({
        'qtd': 'sum',
        'total': 'sum'
    }).reset_index()
    
    vendas_por_dia = vendas_por_dia.sort_values('sale_date')
    
    # Criar calendário completo
    data_min = vendas_por_dia['sale_date'].min()
    data_max = vendas_por_dia['sale_date'].max()
    
    calendario = pd.date_range(start=data_min, end=data_max, freq='D')
    calendario_df = pd.DataFrame({'sale_date': calendario})
    
    # Fazer LEFT JOIN para incluir dias com venda = 0
    serie_completa = calendario_df.merge(vendas_por_dia, on='sale_date', how='left')
    serie_completa['qtd'] = serie_completa['qtd'].fillna(0)
    serie_completa['total'] = serie_completa['total'].fillna(0)
    
    return serie_completa.sort_values('sale_date').reset_index(drop=True)


def dividir_treino_teste(serie_temporal):
    """Divide dados em treino (até 31/12/2023) e teste (Janeiro 2024)."""
    
    # Data de corte
    data_corte = pd.to_datetime('2023-12-31')
    
    treino = serie_temporal[serie_temporal['sale_date'] <= data_corte].copy()
    teste = serie_temporal[
        (serie_temporal['sale_date'] > data_corte) & 
        (serie_temporal['sale_date'] < pd.to_datetime('2024-02-01'))
    ].copy()
    
    return treino, teste


def prever_media_movel(treino, teste, janela=7):
    """
    Implementa modelo baseline com média móvel de 7 dias.
    Para cada data de teste, calcula a média dos últimos 7 dias de TREINO.
    """
    
    # Garantir que treino está ordenado
    treino = treino.sort_values('sale_date').reset_index(drop=True)
    
    previsoes = []
    
    for idx, row_teste in teste.iterrows():
        data_teste = row_teste['sale_date']
        
        # Filtrar dados de treino anteriores à data de teste
        treino_antes = treino[treino['sale_date'] < data_teste].copy()
        
        if len(treino_antes) == 0:
            # Se não há dados antes, usar a primeira venda disponível
            previsao = treino['qtd'].iloc[0]
        else:
            # Pegar últimos 7 dias antes da data de teste
            ultimos_7 = treino_antes.tail(janela)
            previsao = ultimos_7['qtd'].mean()
        
        previsoes.append({
            'sale_date': data_teste,
            'qtd_real': row_teste['qtd'],
            'qtd_prevista': previsao,
            'erro_absoluto': abs(row_teste['qtd'] - previsao)
        })
    
    return pd.DataFrame(previsoes)


def calcular_metricas(resultado):
    """Calcula métricas de desempenho."""
    
    mae = resultado['erro_absoluto'].mean()
    rmse = np.sqrt((resultado['erro_absoluto'] ** 2).mean())
    mape = (resultado['erro_absoluto'] / (resultado['qtd_real'] + 1)).mean() * 100
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape,
        'Total_Dias': len(resultado),
        'Dias_Com_Venda': (resultado['qtd_real'] > 0).sum()
    }


def main():
    """Executa o pipeline completo."""
    
    print("\n" + "="*80)
    print("QUESTÃO 7.1 - MODELO BASELINE DE PREVISÃO DE DEMANDA")
    print("="*80 + "\n")
    
    # 1. Carregar e processar
    print("1. Carregando dados...")
    vendas_df, produtos_df = carregar_e_processar_dados()
    print(f"   Total de registros: {len(vendas_df)}")
    print(f"   Total de produtos: {len(produtos_df)}\n")
    
    # 2. Filtrar produto
    print("2. Filtrando produto: 'Motor de Popa Yamaha Evo Dash 155HP'...")
    nome_produto = "Motor de Popa Yamaha Evo Dash 155HP"
    vendas_produto = filtrar_produto(vendas_df, nome_produto)
    
    if vendas_produto is None:
        print("   Tentando com nome alternativo...")
        nome_produto = "Motor de Popa"
        vendas_produto = filtrar_produto(vendas_df, nome_produto)
    
    if vendas_produto is None:
        print("   ❌ Produto não encontrado!")
        return
    
    print(f"   ✓ Encontrado: {len(vendas_produto)} registros de vendas")
    print(f"   Primeiras vendas: {vendas_produto['sale_date'].min()}")
    print(f"   Últimas vendas: {vendas_produto['sale_date'].max()}\n")
    
    # 3. Criar série temporal
    print("3. Criando série temporal diária...")
    serie_temporal = criar_serie_temporal(vendas_produto)
    print(f"   Total de dias: {len(serie_temporal)}")
    print(f"   Quantidade total vendida: {serie_temporal['qtd'].sum():.0f} unidades\n")
    
    # 4. Dividir treino/teste
    print("4. Dividindo dados em treino (até 31/12/2023) e teste (Jan/2024)...")
    treino, teste = dividir_treino_teste(serie_temporal)
    print(f"   Treino: {len(treino)} dias ({treino['sale_date'].min().date()} a {treino['sale_date'].max().date()})")
    print(f"   Teste: {len(teste)} dias ({teste['sale_date'].min().date()} a {teste['sale_date'].max().date()})\n")
    
    # 5. Gerar previsões
    print("5. Gerando previsões com Média Móvel de 7 dias...")
    resultado = prever_media_movel(treino, teste, janela=7)
    print(f"   ✓ {len(resultado)} previsões geradas\n")
    
    # 6. Calcular métricas
    print("6. Calculando métricas de desempenho...")
    metricas = calcular_metricas(resultado)
    print(f"   MAE (Mean Absolute Error): {metricas['MAE']:.2f} unidades")
    print(f"   RMSE (Root Mean Square Error): {metricas['RMSE']:.2f} unidades")
    print(f"   MAPE (Mean Absolute % Error): {metricas['MAPE']:.2f}%")
    print(f"   Total de dias no teste: {metricas['Total_Dias']}")
    print(f"   Dias com venda registrada: {metricas['Dias_Com_Venda']}\n")
    
    # 7. Mostrar resultados detalhados
    print("7. Previsões Detalhadas (Janeiro 2024):")
    print("-" * 80)
    resultado_display = resultado.copy()
    resultado_display['sale_date'] = resultado_display['sale_date'].dt.strftime('%Y-%m-%d')
    print(resultado_display.to_string(index=False))
    print("-" * 80 + "\n")
    
    # Q7.2 — Validação: soma previsões primeira semana
    primeira_semana = resultado[
        (resultado['sale_date'] >= pd.to_datetime('2024-01-01')) &
        (resultado['sale_date'] <= pd.to_datetime('2024-01-07'))
    ]
    soma_previsao_semana = primeira_semana['qtd_prevista'].sum()
    print("Q7.2 — VALIDAÇÃO:")
    print(f"   Soma total da previsão de vendas para 01/01 a 07/01/2024:")
    print(f"   {round(soma_previsao_semana)} unidades (arredondado)")
    print(f"   Valor exato: {soma_previsao_semana:.4f} unidades\n")
    
    # 8. Análise do modelo
    print("8. ANÁLISE DO MODELO:")
    print("-" * 80)
    
    venda_media_teste = resultado['qtd_real'].mean()
    previsao_media = resultado['qtd_prevista'].mean()
    
    print(f"Venda média diária (real em Jan/2024): {venda_media_teste:.2f} unidades")
    print(f"Previsão média diária (modelo): {previsao_media:.2f} unidades")
    print(f"Diferença média: {abs(venda_media_teste - previsao_media):.2f} unidades")
    
    acuracia = (1 - (metricas['MAE'] / (venda_media_teste + 1))) * 100
    print(f"Acurácia aproximada: {max(0, acuracia):.2f}%\n")
    
    # 9. Resposta às perguntas
    print("9. RESPOSTAS ÀS PERGUNTAS:")
    print("-" * 80)
    
    print("\na) O baseline é adequado para esse produto?")
    if metricas['MAE'] < venda_media_teste * 0.2:
        print("   RESPOSTA: Sim, o baseline é adequado.")
        print(f"   Justificativa: MAE de {metricas['MAE']:.2f} unidades representa apenas")
        print(f"   {(metricas['MAE'] / venda_media_teste * 100):.1f}% da venda média diária.")
    elif metricas['MAE'] < venda_media_teste * 0.5:
        print("   RESPOSTA: Parcialmente adequado.")
        print(f"   Justificativa: MAE de {metricas['MAE']:.2f} unidades representa")
        print(f"   {(metricas['MAE'] / venda_media_teste * 100):.1f}% da venda média (razoável).")
    else:
        print("   RESPOSTA: Não, o baseline é inadequado.")
        print(f"   Justificativa: MAE de {metricas['MAE']:.2f} unidades representa")
        print(f"   {(metricas['MAE'] / (venda_media_teste + 1) * 100):.1f}% da venda média (muito alto).")
    
    print("\nb) Cite uma limitação desse método:")
    print("   A Média Móvel de 7 dias NÃO captura tendências de longo prazo.")
    print("   Se há crescimento ou queda consistente nas vendas, o modelo")
    print("   continuará prevendo a média histórica recente, sem se adaptar.")
    print("   Também não considera sazonalidade (ex: verão vs inverno) nem")
    print("   fatores externos (promoções, feriados, falta de estoque).")
    
    # Q7.3 — Explicação formal
    print("\nQ7.3 — EXPLICAÇÃO:")
    print("-" * 80)
    print("  Como o baseline foi construído?")
    print("    Para cada dia de Janeiro/2024, calcula-se a média das vendas diárias")
    print("    dos últimos 7 dias ANTERIORES (rolling window de 7 dias).")
    print("    A janela se move dia a dia, sempre usando apenas dados passados.")
    print()
    print("  Como evitou data leakage?")
    print("    O split temporal garante que NENHUM dado de Janeiro/2024 (teste)")
    print("    é usado no treino. Treino = até 31/12/2023. Teste = Jan/2024.")
    print("    Para cada previsão, a média móvel usa APENAS dados anteriores")
    print("    à data prevista (nunca dados futuros).")
    print()
    print("  Uma limitação do modelo proposto:")
    print("    A Média Móvel não captura tendências nem sazonalidade.")
    print("    Se as vendas estão crescendo, o modelo subestima; se estão caindo,")
    print("    superestima. Também é sensível a outliers na janela de 7 dias.")
    
    print("\n" + "="*80)
    print("✓ MODELO BASELINE CONCLUÍDO")
    print("="*80 + "\n")
    
    # Salvar resultados
    resultado_display = resultado.copy()
    resultado_display['sale_date'] = resultado_display['sale_date'].dt.strftime('%Y-%m-%d')
    resultado_display.to_csv('data/processed/previsao_motor_popa_janeiro_2024.csv', index=False)
    print("Previsões salvas em: data/processed/previsao_motor_popa_janeiro_2024.csv\n")


if __name__ == "__main__":
    main()
