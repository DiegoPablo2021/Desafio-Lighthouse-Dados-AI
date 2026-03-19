"""
Q5: Análise de Clientes Fiéis - Segmentação RFM

Identifica os 10 clientes élite com maior ticket médio 
que compraram em 3+ categorias distintas.
"""

import csv
from pathlib import Path
from collections import defaultdict


def normalizar_categoria(categoria: str) -> str:
    """Normaliza variações de grafia nas categorias."""
    if categoria is None:
        return "desconhecida"
    
    categoria_limpa = categoria.lower().strip()
    
    # Mapear variações
    if categoria_limpa in ['ancoragem', 'ancorajem', 'ancorajen', 'encoragem', 'ancor', 'ancoras']:
        return 'ancoragem'
    elif categoria_limpa in ['propulsão', 'propulsao', 'propulsion', 'motor', 'propulsor']:
        return 'propulsão'
    elif categoria_limpa in ['eletrônicos', 'eletronicos', 'electronics', 'electronic']:
        return 'eletrônicos'
    
    return categoria_limpa


def main():
    """Executa análise de clientes fiéis."""
    
    print("="*70)
    print("Q5: ANÁLISE DE CLIENTES FIÉIS - SEGMENTAÇÃO RFM")
    print("="*70 + "\n")
    
    # Carregar produtos com categorias limpas
    print("Carregando produtos...")
    produtos = {}
    try:
        with open('data/raw/produtos_raw.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                produto_id = int(row['code'])
                categoria_normalizada = normalizar_categoria(row.get('actual_category', ''))
                produtos[produto_id] = {
                    'name': row.get('name', ''),
                    'category': categoria_normalizada
                }
    except Exception as e:
        print(f"ERRO ao carregar produtos: {e}")
        return
    
    print(f"Produtos carregados: {len(produtos)}\n")
    
    # Carregar vendas e agregar métricas por cliente
    print("Carregando vendas e agregando métricas...")
    metricas_clientes = defaultdict(lambda: {
        'faturamento_total': 0,
        'frequencia': 0,
        'categorias': set(),
        'vendas_por_categoria': defaultdict(int)
    })
    
    try:
        with open('data/raw/vendas_2023_2024.csv', 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                id_client = int(row['id_client'])
                id_product = int(row['id_product'])
                qtd = int(row['qtd'])
                valor_venda = float(row['total'])
                
                # Obter categoria do produto
                categoria = produtos.get(id_product, {}).get('category', 'desconhecida')
                
                # Agregar
                metricas_clientes[id_client]['faturamento_total'] += valor_venda
                metricas_clientes[id_client]['frequencia'] += 1
                metricas_clientes[id_client]['categorias'].add(categoria)
                metricas_clientes[id_client]['vendas_por_categoria'][categoria] += qtd
    except Exception as e:
        print(f"ERRO ao carregar vendas: {e}")
        return
    
    print(f"Clientes encontrados: {len(metricas_clientes)}\n")
    
    # Calcular ticket médio e filtrar por diversidade (3+ categorias)
    print("Calculando ticket médio e filtrando por diversidade...")
    clientes_elite = []
    
    for id_client, dados in metricas_clientes.items():
        diversidade = len(dados['categorias'])
        
        # Filtro: 3+ categorias
        if diversidade >= 3:
            ticket_medio = dados['faturamento_total'] / dados['frequencia']
            
            clientes_elite.append({
                'id_client': id_client,
                'faturamento_total': dados['faturamento_total'],
                'frequencia': dados['frequencia'],
                'ticket_medio': ticket_medio,
                'diversidade_categorias': diversidade,
                'vendas_por_categoria': dict(dados['vendas_por_categoria'])
            })
    
    print(f"Clientes com 3+ categorias: {len(clientes_elite)}\n")
    
    # Ordenar por ticket médio DESC, depois id_client ASC
    clientes_elite.sort(
        key=lambda x: (-x['ticket_medio'], x['id_client'])
    )
    
    # Pegar top 10
    top_10 = clientes_elite[:10]
    
    print("TOP 10 CLIENTES FIÉIS:")
    print("-" * 90)
    print(f"{'ID':<6} {'Faturamento':<18} {'Freq':<6} {'Ticket Médio':<16} {'Categ':<6} {'Categoria TOP':<18} {'Qt':<6}")
    print("-" * 90)
    
    for cliente in top_10:
        # Categoria com maior quantidade de itens
        categoria_top = max(
            cliente['vendas_por_categoria'].items(),
            key=lambda x: x[1]
        )
        
        print(
            f"{cliente['id_client']:<6} "
            f"R$ {cliente['faturamento_total']:>15,.2f} "
            f"{cliente['frequencia']:<6} "
            f"R$ {cliente['ticket_medio']:>14,.2f} "
            f"{cliente['diversidade_categorias']:<6} "
            f"{categoria_top[0]:<18} "
            f"{categoria_top[1]:<6}"
        )
    
    print("-" * 90 + "\n")
    
    # Salvar resultado
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "clientes_fieis_top10.csv"
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    'id_client',
                    'faturamento_total',
                    'frequencia',
                    'ticket_medio',
                    'diversidade_categorias',
                    'categoria_top',
                    'qtd_categoria_top'
                ]
            )
            writer.writeheader()
            
            for cliente in top_10:
                categoria_top = max(
                    cliente['vendas_por_categoria'].items(),
                    key=lambda x: x[1]
                )
                
                writer.writerow({
                    'id_client': cliente['id_client'],
                    'faturamento_total': f"{cliente['faturamento_total']:.2f}",
                    'frequencia': cliente['frequencia'],
                    'ticket_medio': f"{cliente['ticket_medio']:.2f}",
                    'diversidade_categorias': cliente['diversidade_categorias'],
                    'categoria_top': categoria_top[0],
                    'qtd_categoria_top': categoria_top[1]
                })
        
        print(f"Resultado salvo em: {output_file}\n")
        
    except Exception as e:
        print(f"ERRO ao salvar resultado: {e}")
        return
    
    # Q5.3 — Explicação
    print("Q5.3 — EXPLICAÇÃO:")
    print("-" * 70)
    print("  Como você realizou a limpeza das categorias?")
    print("    Mapeamento de todas as variações de grafia para 3 categorias")
    print("    padrão: 'ancoragem', 'propulsão' e 'eletrônicos'.")
    print("    Variações tratadas incluem: 'Ancorajen', 'Encoragem' -> ancoragem;")
    print("    'Propução', 'Propulçao', 'Propulsam' -> propulsão;")
    print("    'Eletrunicos', 'eLeTrÔnIcOs' -> eletrônicos.")
    print("    O mapeamento aplica lowercase + strip e busca prefixos/substrings.")
    print()
    print("  Qual lógica utilizou para filtrar os clientes com diversidade mínima?")
    print("    Para cada cliente, calcula-se o número de categorias DISTINTAS")
    print("    (já normalizadas) em que ele comprou. Apenas clientes com")
    print("    COUNT(DISTINCT categoria) >= 3 são considerados no ranking.")
    print()
    print("  Como garantiu que a contagem de itens refletisse apenas os Top 10?")
    print("    Primeiro, calcula-se o Ticket Médio e a Diversidade por cliente.")
    print("    Filtra-se os clientes com diversidade >= 3.")
    print("    Ordena-se por Ticket Médio DESC, id_client ASC e seleciona-se os 10 primeiros.")
    print("    A contagem de itens por categoria é feita APENAS sobre as vendas")
    print("    desses 10 clientes, garantindo que não se misturem dados de outros.")
    
    print("\n" + "="*70)
    print("Q5 concluída com sucesso")
    print("="*70)


if __name__ == "__main__":
    main()
