"""
Q4: Análise de Prejuízo por Produto

Identifica produtos vendidos abaixo do custo considerando:
- Custo em USD por produto (do arquivo custos_importacao.json)
- Taxa de câmbio USD/BRL do dia da venda (API do Banco Central)
- Cálculo: custo_brl = custo_usd * taxa_cambio * quantidade

Premissas obrigatórias:
  - Custo USD é unitário
  - Câmbio = média da cotação de venda do dia (Banco Central - PTAX)
  - Receita total considera TODAS as vendas
  - Ignorar impostos e frete
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

import pandas as pd
import requests
import matplotlib
matplotlib.use('Agg')  # Backend nao-interativo (sem janela)
import matplotlib.pyplot as plt


# ---------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------

def parse_data(data_str: str) -> datetime:
    """Converte data em diferentes formatos para datetime."""
    for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']:
        try:
            return datetime.strptime(data_str, fmt)
        except ValueError:
            continue
    return None


def obter_custo_produto(product_id: int, data_venda: datetime, custos_historico: dict) -> float:
    """Obtém o custo USD mais recente anterior ou igual à data de venda."""
    if product_id not in custos_historico:
        return None

    custos_ordenados = sorted(
        custos_historico[product_id],
        key=lambda x: x['data'],
        reverse=True
    )

    for custo in custos_ordenados:
        if custo['data'] <= data_venda:
            return float(custo['usd_price'])

    # Se nenhum custo anterior, usar o mais antigo disponível
    if custos_ordenados:
        return float(custos_ordenados[-1]['usd_price'])

    return None


def obter_cambio_bcb(data_inicio: str, data_fim: str) -> dict:
    """
    Obtém a taxa de câmbio USD/BRL (cotação de venda - PTAX)
    do Banco Central do Brasil via API pública.

    Retorna dict {date_str: taxa_media_venda}
    """
    print("  Consultando API do Banco Central (PTAX)...")

    # API PTAX do BCB - cotação de venda do dólar
    url = (
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/"
        "odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
        f"?@dataInicial='{data_inicio}'&@dataFinalCotacao='{data_fim}'"
        "&$top=10000&$format=json"
        "&$select=cotacaoVenda,dataHoraCotacao"
    )

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        dados = response.json()['value']
    except Exception as e:
        print(f"  ERRO ao consultar BCB: {e}")
        print("  Usando fallback: arquivo local de câmbio ou taxa média.")
        return None

    # Agrupar por data e calcular média da cotação de venda
    cambio_por_dia = defaultdict(list)
    for cotacao in dados:
        data_str = cotacao['dataHoraCotacao'][:10]  # "2023-01-02 ..."
        # Converter formato da data BCB
        try:
            dt = datetime.strptime(data_str, '%Y-%m-%d')
        except ValueError:
            continue
        cambio_por_dia[dt.strftime('%Y-%m-%d')].append(cotacao['cotacaoVenda'])

    # Média das cotações de venda por dia
    cambio_medio = {}
    for data, cotacoes in cambio_por_dia.items():
        cambio_medio[data] = sum(cotacoes) / len(cotacoes)

    print(f"  Cotações obtidas: {len(cambio_medio)} dias")
    return cambio_medio


def obter_taxa_para_data(data_venda: datetime, cambio_dict: dict) -> float:
    """
    Retorna a taxa de câmbio para a data da venda.
    Se não houver cotação no dia (fins de semana/feriados),
    utiliza a cotação do último dia útil anterior.
    """
    data_str = data_venda.strftime('%Y-%m-%d')

    # Procurar a data exata primeiro
    if data_str in cambio_dict:
        return cambio_dict[data_str]

    # Se não encontrou, buscar o dia útil anterior mais próximo (até 7 dias)
    for i in range(1, 8):
        data_anterior = (data_venda - timedelta(days=i)).strftime('%Y-%m-%d')
        if data_anterior in cambio_dict:
            return cambio_dict[data_anterior]

    return None


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------

def main():
    """Executa análise de prejuízo com câmbio diário do BCB."""

    print("=" * 70)
    print("Q4: ANÁLISE DE PREJUÍZO POR PRODUTO")
    print("=" * 70 + "\n")

    # 1. Carregar custos de importação
    print("1. Carregando dados de custos de importação...")
    custos_historico = defaultdict(list)

    try:
        with open('data/raw/custos_importacao.json', 'r', encoding='utf-8') as f:
            data_custos = json.load(f)

        for produto in data_custos:
            product_id = int(produto['product_id'])
            if 'historic_data' in produto:
                for entrada in produto['historic_data']:
                    data = parse_data(entrada.get('start_date', ''))
                    if data:
                        custos_historico[product_id].append({
                            'data': data,
                            'usd_price': float(entrada['usd_price'])
                        })
    except Exception as e:
        print(f"  ERRO ao carregar custos: {e}")
        return

    print(f"  Custos carregados para {len(custos_historico)} produtos\n")

    # 2. Carregar vendas
    print("2. Carregando dados de vendas...")
    df_vendas = pd.read_csv('data/raw/vendas_2023_2024.csv')
    df_vendas['sale_date'] = pd.to_datetime(df_vendas['sale_date'], format='mixed')
    print(f"  Vendas carregadas: {len(df_vendas)} registros")

    data_min = df_vendas['sale_date'].min()
    data_max = df_vendas['sale_date'].max()
    print(f"  Período: {data_min.date()} a {data_max.date()}\n")

    # 3. Obter câmbio do BCB
    print("3. Obtendo taxa de câmbio (PTAX) do Banco Central...")
    cambio_dict = obter_cambio_bcb(
        data_inicio=f"{(data_min - timedelta(days=10)).strftime('%m-%d-%Y')}",
        data_fim=f"{data_max.strftime('%m-%d-%Y')}"
    )

    if cambio_dict is None:
        print("  FALLBACK: Usando tabela de câmbio simplificada.")
        # Fallback: gerar tabela com taxa média caso a API falhe
        print("  AVISO: Resultados podem ser imprecisos sem câmbio real.\n")
        # Usar taxa média do período como fallback
        taxa_fallback = 5.0
        print(f"  Taxa fallback: R$ {taxa_fallback}")
        cambio_dict = {}
        usar_fallback = True
    else:
        usar_fallback = False
        # Mostrar amostra de cotações
        amostra = sorted(cambio_dict.items())[:5]
        print(f"  Amostra de cotações:")
        for data, taxa in amostra:
            print(f"    {data}: R$ {taxa:.4f}")
        print()

    # 4. Análise de prejuízo
    print("4. Calculando prejuízos por transação...\n")

    prejuizo_por_produto = defaultdict(lambda: {
        'receita_total': 0.0,
        'custo_total_brl': 0.0,
        'prejuizo_total': 0.0,
        'vendas_com_prejuizo': 0,
        'total_vendas': 0,
        'taxas_utilizadas': []
    })

    transacoes_sem_cambio = 0
    transacoes_sem_custo = 0

    for _, venda in df_vendas.iterrows():
        product_id = int(venda['id_product'])
        data_venda = venda['sale_date'].to_pydatetime()
        qtd = int(venda['qtd'])
        valor_venda = float(venda['total'])

        # Obter custo USD
        custo_usd = obter_custo_produto(product_id, data_venda, custos_historico)
        if custo_usd is None:
            transacoes_sem_custo += 1
            continue

        # Obter câmbio do dia
        if usar_fallback:
            taxa = taxa_fallback
        else:
            taxa = obter_taxa_para_data(data_venda, cambio_dict)
            if taxa is None:
                transacoes_sem_cambio += 1
                continue

        # Calcular custo total em BRL (custo unitário × câmbio × quantidade)
        custo_total_brl = custo_usd * taxa * qtd
        prejuizo = max(0, custo_total_brl - valor_venda)

        # Agregar por produto
        prejuizo_por_produto[product_id]['receita_total'] += valor_venda
        prejuizo_por_produto[product_id]['custo_total_brl'] += custo_total_brl
        prejuizo_por_produto[product_id]['prejuizo_total'] += prejuizo
        prejuizo_por_produto[product_id]['total_vendas'] += 1
        prejuizo_por_produto[product_id]['taxas_utilizadas'].append(taxa)

        if prejuizo > 0:
            prejuizo_por_produto[product_id]['vendas_com_prejuizo'] += 1

    if transacoes_sem_custo > 0:
        print(f"  Transações sem custo USD encontrado: {transacoes_sem_custo}")
    if transacoes_sem_cambio > 0:
        print(f"  Transações sem câmbio disponível: {transacoes_sem_cambio}")

    # 5. Filtrar e exibir produtos com prejuízo
    produtos_com_prejuizo = {
        pid: dados
        for pid, dados in prejuizo_por_produto.items()
        if dados['prejuizo_total'] > 0
    }

    print(f"\n  Produtos analisados: {len(prejuizo_por_produto)}")
    print(f"  Produtos COM prejuízo: {len(produtos_com_prejuizo)}\n")

    print("RESULTADO — Produtos com Prejuízo:")
    print("-" * 85)
    print(f"{'ID Produto':<12} {'Receita (BRL)':<18} {'Prejuízo (BRL)':<18} {'% Perda':<10} {'Câmbio Médio':<12}")
    print("-" * 85)

    # Ordenar por prejuízo decrescente
    ranking = sorted(
        produtos_com_prejuizo.items(),
        key=lambda x: x[1]['prejuizo_total'],
        reverse=True
    )

    for product_id, dados in ranking:
        percentual = (dados['prejuizo_total'] / dados['receita_total'] * 100) if dados['receita_total'] > 0 else 0
        cambio_medio = sum(dados['taxas_utilizadas']) / len(dados['taxas_utilizadas']) if dados['taxas_utilizadas'] else 0

        print(
            f"{product_id:<12} "
            f"R$ {dados['receita_total']:>15,.2f} "
            f"R$ {dados['prejuizo_total']:>15,.2f} "
            f"{percentual:>8.2f}% "
            f"R$ {cambio_medio:>8.4f}"
        )

    print("-" * 85)

    # 6. Respostas objetivas (Q4 Parte 3)
    print("\nQ4 — RESPOSTAS OBJETIVAS:")
    print("-" * 70)

    if ranking:
        maior_prejuizo_id = ranking[0][0]
        maior_prejuizo_dados = ranking[0][1]
        pct_maior = (maior_prejuizo_dados['prejuizo_total'] / maior_prejuizo_dados['receita_total'] * 100) if maior_prejuizo_dados['receita_total'] > 0 else 0

        # Encontrar produto com maior % de perda
        produto_maior_pct = max(
            produtos_com_prejuizo.items(),
            key=lambda x: (x[1]['prejuizo_total'] / x[1]['receita_total'] * 100) if x[1]['receita_total'] > 0 else 0
        )
        maior_pct_id = produto_maior_pct[0]
        maior_pct_valor = (produto_maior_pct[1]['prejuizo_total'] / produto_maior_pct[1]['receita_total'] * 100)

        print(f"  a) Produto com MAIOR prejuízo absoluto: ID {maior_prejuizo_id}")
        print(f"     Prejuízo: R$ {maior_prejuizo_dados['prejuizo_total']:,.2f}")
        print()
        print(f"  b) O produto com maior prejuízo absoluto também é o com maior % de perda?")
        if maior_prejuizo_id == maior_pct_id:
            print(f"     SIM. O produto ID {maior_prejuizo_id} tem tanto o maior prejuízo")
            print(f"     absoluto quanto a maior porcentagem de perda ({pct_maior:.2f}%).")
        else:
            print(f"     NÃO. O maior prejuízo absoluto é do produto {maior_prejuizo_id} ({pct_maior:.2f}%),")
            print(f"     mas a maior porcentagem de perda é do produto {maior_pct_id} ({maior_pct_valor:.2f}%).")
    else:
        print("  Nenhum produto com prejuízo identificado.")

    # 7. Q4.3 — Interpretação
    print("\nQ4.3 — INTERPRETAÇÃO:")
    print("-" * 70)
    if usar_fallback:
        print("  Câmbio utilizado: Taxa fixa de R$ 5,00 (fallback — API BCB indisponível)")
    else:
        print("  Câmbio utilizado: Média da cotação de VENDA do dólar (PTAX) do dia")
        print("    da transação, obtida via API do Banco Central do Brasil.")
        print("    Para dias sem cotação (fins de semana/feriados), foi utilizada a")
        print("    cotação do último dia útil anterior.")
    print()
    print("  Definição de prejuízo: Uma transação tem prejuízo quando o custo total")
    print("    em BRL (custo_usd × câmbio_do_dia × quantidade) é MAIOR que o valor")
    print("    de venda em BRL registrado.")
    print()
    print("  Suposições relevantes:")
    print("    - O custo USD utilizado é o mais recente anterior à data da venda")
    print("      (conforme histórico de preços do fornecedor)")
    print("    - Não foram considerados impostos, frete ou outros custos operacionais")
    print("    - A receita total por produto inclui TODAS as vendas (com e sem prejuízo)")

    # 8. Q4 Parte 2 - Grafico de prejuizo por produto
    print("\nQ4 PARTE 2 - GERANDO GRAFICO DE PREJUIZO...")
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    if ranking:
        # Carregar nomes dos produtos
        try:
            produtos_df = pd.read_csv('data/raw/produtos_raw.csv')
            nomes = dict(zip(produtos_df['code'], produtos_df['name']))
        except Exception:
            nomes = {}

        ids = [str(pid) for pid, _ in ranking]
        labels = [nomes.get(int(pid), f"Produto {pid}")[:30] for pid in ids]
        prejuizos = [dados['prejuizo_total'] for _, dados in ranking]

        fig, ax = plt.subplots(figsize=(12, max(4, len(ranking) * 0.6)))
        bars = ax.barh(range(len(labels)), prejuizos, color='#e74c3c', edgecolor='#c0392b')
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel('Prejuizo Total (R$)', fontsize=11)
        ax.set_title('Prejuizo Total por Produto (apenas produtos com prejuizo)', fontsize=13, fontweight='bold')
        ax.invert_yaxis()

        # Adicionar valores nas barras
        for i, (bar, val) in enumerate(zip(bars, prejuizos)):
            ax.text(bar.get_width() + max(prejuizos) * 0.01, bar.get_y() + bar.get_height() / 2,
                    f'R$ {val:,.2f}', va='center', fontsize=8)

        plt.tight_layout()
        grafico_path = output_dir / "grafico_prejuizo_produto.png"
        fig.savefig(grafico_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"  Grafico salvo em: {grafico_path}")
    else:
        print("  Nenhum produto com prejuizo para gerar grafico.")

    # 9. Salvar resultado CSV
    output_file = output_dir / "prejuizo_produtos.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['product_id', 'receita_total_brl', 'prejuizo_total_brl', 'percentual_perda']
        )
        writer.writeheader()

        for product_id, dados in ranking:
            percentual = (dados['prejuizo_total'] / dados['receita_total'] * 100) if dados['receita_total'] > 0 else 0
            writer.writerow({
                'product_id': product_id,
                'receita_total_brl': f"{dados['receita_total']:.2f}",
                'prejuizo_total_brl': f"{dados['prejuizo_total']:.2f}",
                'percentual_perda': f"{percentual:.2f}"
            })

    print(f"\nResultado salvo em: {output_file}")

    print("\n" + "=" * 70)
    print("Q4 concluída com sucesso")
    print("=" * 70)


if __name__ == "__main__":
    main()
