"""
QUESTÃO 8.1 - SISTEMA DE RECOMENDAÇÃO
Motor de Recomendação baseado em Similaridade de Compra

Objetivo: Identificar os 5 produtos mais similares ao "GPS Garmin Vortex Maré Drift"
baseado na similaridade de comportamento de compra dos clientes.

Método: Matriz Usuário × Produto com Similaridade de Cosseno
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')


def carregar_dados():
    """Carrega datasets de vendas e produtos."""
    print("Carregando dados...")
    vendas_df = pd.read_csv('data/raw/vendas_2023_2024.csv')
    produtos_df = pd.read_csv('data/raw/produtos_raw.csv')
    
    return vendas_df, produtos_df


def criar_matriz_usuario_produto(vendas_df):
    """
    Cria matriz de interação Usuário × Produto.
    
    Linhas: id_cliente
    Colunas: id_produto
    Valor: 1 (cliente comprou) ou 0 (cliente não comprou)
    """
    print("Criando matriz de interação Usuário × Produto...")
    
    # Criando matriz com presença/ausência (1/0)
    # Agrupando por cliente e produto, verificando se houver compra
    compras = vendas_df.groupby(['id_client', 'id_product']).size().reset_index(name='comprou')
    compras['comprou'] = 1  # Converter para 1 (houve compra)
    
    # Criando matriz pivot
    matriz_usuario_produto = compras.pivot_table(
        index='id_client',
        columns='id_product',
        values='comprou',
        fill_value=0,
        aggfunc='max'
    )
    
    print(f"Matriz criada: {matriz_usuario_produto.shape[0]} clientes × {matriz_usuario_produto.shape[1]} produtos")
    
    return matriz_usuario_produto


def calcular_similaridade_coseno(matriz_usuario_produto):
    """
    Calcula similaridade de cosseno entre todos os produtos.
    
    A similaridade é calculada com base nos clientes que compraram cada produto.
    Produto A é similar a Produto B se clientes similares compraram ambos.
    """
    print("Calculando similaridade de cosseno entre produtos...")
    
    # Transpor para ter produtos como linhas
    matriz_produto_usuario = matriz_usuario_produto.T
    
    # Calculando similaridade de cosseno (produto x produto)
    similaridade = cosine_similarity(matriz_produto_usuario)
    
    # Convertendo para DataFrame para facilitar a manipulação
    similaridade_df = pd.DataFrame(
        similaridade,
        index=matriz_produto_usuario.index,
        columns=matriz_produto_usuario.index
    )
    
    print(f"Matriz de similaridade calculada: {similaridade_df.shape}")
    
    return similaridade_df


def encontrar_produto_referencia(produtos_df, nome_produto):
    """Encontra o id_produto do GPS Garmin."""
    print(f"Procurando produto: '{nome_produto}'...")
    
    # Procurando por nome
    produto_encontrado = produtos_df[
        produtos_df['name'].str.contains(nome_produto, case=False, na=False)
    ]
    
    if len(produto_encontrado) == 0:
        print(f"⚠ Produto '{nome_produto}' não encontrado exatamente.")
        print("Produtos similares:")
        gps_products = produtos_df[
            produtos_df['name'].str.contains('GPS', case=False, na=False)
        ]
        for idx, row in gps_products.iterrows():
            print(f"  - {row['code']}: {row['name']}")
        return None
    
    produto_id = produto_encontrado.iloc[0]['code']
    print(f"✓ Encontrado: ID {produto_id} - {produto_encontrado.iloc[0]['name']}")
    
    return produto_id


def gerar_ranking_similar(similaridade_df, produto_id, top_n=5):
    """
    Gera ranking dos N produtos mais similares.
    
    Desconsdera o próprio produto.
    """
    print(f"\nGerando ranking dos {top_n} produtos mais similares...")
    
    # Obtendo similaridades do produto de referência
    similaridades_produto = similaridade_df[produto_id].sort_values(ascending=False)
    
    # Removendo o próprio produto
    similaridades_produto = similaridades_produto[similaridades_produto.index != produto_id]
    
    # Pegando top "N"
    top_similares = similaridades_produto.head(top_n)
    
    return top_similares


def obter_nomes_produtos(produto_ids, produtos_df):
    """Obter nomes dos produtos a partir dos IDs."""
    nomes = {}
    for prod_id in produto_ids:
        prod_info = produtos_df[produtos_df['code'] == prod_id]
        if len(prod_info) > 0:
            nomes[prod_id] = prod_info.iloc[0]['name']
        else:
            nomes[prod_id] = f"ID {prod_id}"
    return nomes


def main():
    """Executa o pipeline completo de recomendação."""
    
    print("\n" + "="*80)
    print("QUESTÃO 8.1 - SISTEMA DE RECOMENDAÇÃO")
    print("Motor de Recomendação baseado em Similaridade de Compra")
    print("="*80 + "\n")
    
    # 1. Carregando dados
    vendas_df, produtos_df = carregar_dados()
    print(f"   Registros de vendas: {len(vendas_df)}")
    print(f"   Total de produtos: {len(produtos_df)}\n")
    
    # 2. Criando matriz usuário × produto
    matriz_usuario_produto = criar_matriz_usuario_produto(vendas_df)
    print(f"   Clientes únicos: {matriz_usuario_produto.shape[0]}")
    print(f"   Produtos únicos: {matriz_usuario_produto.shape[1]}\n")
    
    # 3. Calculando similaridade de cosseno
    similaridade_df = calcular_similaridade_coseno(matriz_usuario_produto)
    
    # 4. Encontrando produto de referência
    nome_referencia = "GPS Garmin Vortex Maré Drift"
    produto_id_ref = encontrar_produto_referencia(produtos_df, nome_referencia)
    
    if produto_id_ref is None:
        print("Produto não encontrado. Abortando.")
        return
    
    # 5. Gerando ranking
    top_similares = gerar_ranking_similar(similaridade_df, produto_id_ref, top_n=5)
    
    # 6. Obtendo nomes dos produtos
    nomes_produtos = obter_nomes_produtos(top_similares.index.tolist(), produtos_df)
    
    # 7. Exibindo resultados
    print("\n" + "="*80)
    print(f"TOP 5 PRODUTOS SIMILARES A: {nome_referencia}")
    print("="*80 + "\n")
    
    print(f"{'Posição':<10} {'ID Produto':<12} {'Similaridade':<15} {'Nome do Produto':<50}")
    print("-" * 80)
    
    recomendacoes = []
    for idx, (prod_id, similaridade) in enumerate(top_similares.items(), 1):
        nome = nomes_produtos[prod_id]
        print(f"{idx:<10} {prod_id:<12} {similaridade:.4f}          {nome:<50}")
        recomendacoes.append({
            'posicao': idx,
            'id_produto': prod_id,
            'nome_produto': nome,
            'similaridade': similaridade
        })
    
    print("-" * 80)
    
    # 8. Resposta final
    print("\n" + "="*80)
    print("RESPOSTA FINAL - PRODUTO RECOMENDADO")
    print("="*80)
    
    produto_recomendado = recomendacoes[0]
    print(f"\n🎯 RECOMENDAÇÃO PRINCIPAL:")
    print(f"   Posição: {produto_recomendado['posicao']}")
    print(f"   ID: {produto_recomendado['id_produto']}")
    print(f"   Produto: {produto_recomendado['nome_produto']}")
    print(f"   Similaridade: {produto_recomendado['similaridade']:.4f}")
    
    print(f"\n💡 INTERPRETAÇÃO:")
    print(f"   O produto com ID {produto_recomendado['id_produto']} é o mais similar ao GPS.")
    print(f"   Clientes que compraram GPS também compraram este produto com frequência similar.")
    print(f"   Similaridade de {produto_recomendado['similaridade']:.2%} indica forte correlação.")
    
    print("\n📊 RANKING COMPLETO:")
    for rec in recomendacoes:
        print(f"   {rec['posicao']}. {rec['id_produto']} - {rec['nome_produto']} ({rec['similaridade']:.4f})")
    
    print("\n" + "="*80 + "\n")
    
    # 9. Salvando os resultados
    resultado_df = pd.DataFrame(recomendacoes)
    resultado_df.to_csv('data/processed/recomendacoes_gps_garmin.csv', index=False)
    print("✓ Recomendações salvas em: data/processed/recomendacoes_gps_garmin.csv\n")
    
    # Q8.2 — Validação
    print("Q8.2 — VALIDAÇÃO:")
    print(f"   Produto com MAIOR similaridade ao '{nome_referencia}':")
    print(f"   ID: {produto_recomendado['id_produto']}")
    print(f"   Nome: {produto_recomendado['nome_produto']}")
    print(f"   Similaridade: {produto_recomendado['similaridade']:.4f}\n")
    
    # Q8.3 — Explicação
    print("Q8.3 — EXPLICAÇÃO:")
    print("-" * 80)
    print("  Como a matriz foi construída?")
    print("    Criou-se uma matriz binária Usuário × Produto onde cada célula")
    print("    contém 1 se o cliente comprou ao menos uma vez o produto, e 0")
    print("    caso contrário. A quantidade comprada é IGNORADA — apenas")
    print("    presença (1) ou ausência (0) é considerada.")
    print()
    print("  O que significa a similaridade de cosseno nesse contexto?")
    print("    Cada produto é representado por um vetor de clientes que o compraram.")
    print("    A similaridade de cosseno mede o ângulo entre dois vetores de produtos.")
    print("    Quanto mais próximo de 1, mais os produtos compartilham os MESMOS")
    print("    clientes compradores. Similaridade = 1 indica que exatamente os")
    print("    mesmos clientes compraram ambos os produtos. Similaridade = 0")
    print("    indica que nenhum cliente comprou ambos.")
    print()
    print("  Uma limitação desse método de recomendação:")
    print("    O método depende apenas de co-ocorrência de compra (quem comprou")
    print("    X também comprou Y). Ele NÃO considera:")
    print("    - Características dos produtos (preço, categoria, função)")
    print("    - Quantidade comprada")
    print("    - Ordem temporal das compras")
    print("    - Satisfação do cliente")
    print("    Em datasets com poucos clientes (como o atual com 49), a")
    print("    similaridade pode ser instável e sensível a poucos compradores.")
    
    print("\n" + "="*80 + "\n")
    
    # Retornando ID do produto recomendado
    return produto_recomendado['id_produto']


if __name__ == "__main__":
    main()
