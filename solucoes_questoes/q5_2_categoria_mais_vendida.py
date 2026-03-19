"""
QUESTÃO 5.2 - Categoria Mais Vendida pelo Top 10
Identifica qual categoria teve a maior quantidade total de itens
considerando apenas as compras dos Top 10 clientes.
"""

import pandas as pd
import os

# Carregar dados
vendas_df = pd.read_csv('data/raw/vendas_2023_2024.csv')
produtos_df = pd.read_csv('data/raw/produtos_raw.csv')

# Função para normalizar categorias
def normalizar_categoria(cat):
    if pd.isna(cat):
        return 'N/A'
    cat = str(cat).strip().upper()
    
    if cat in ['ANCORAJEN', 'ENCORAGEM', 'ANCORAGEM']:
        return 'ANCORAGEM'
    elif cat in ['ELETRONICO', 'ELETRONICOS']:
        return 'ELETRÔNICOS'
    elif cat in ['PROPULSAO', 'PROPULSÃO']:
        return 'PROPULSÃO'
    return cat

# Aplicar normalização
produtos_df['categoria_normalizada'] = produtos_df['actual_category'].apply(normalizar_categoria)

# Merge vendas com produtos
vendas_com_categoria = vendas_df.merge(
    produtos_df[['code', 'categoria_normalizada']], 
    left_on='id_product', 
    right_on='code', 
    how='inner'
)

# Calcular métricas por cliente
metricas_cliente = vendas_com_categoria.groupby('id_client').agg(
    faturamento_total=('total', 'sum'),
    frequencia=('id', 'count'),
    diversidade_categorias=('categoria_normalizada', 'nunique')
).reset_index()

metricas_cliente['ticket_medio'] = metricas_cliente['faturamento_total'] / metricas_cliente['frequencia']

# Filtrar com 3+ categorias
clientes_com_3_categorias = metricas_cliente[metricas_cliente['diversidade_categorias'] >= 3]

# Top 10 por ticket médio
top_10 = clientes_com_3_categorias.nlargest(10, 'ticket_medio')['id_client'].values

print(f"\n🔍 TOP 10 CLIENTES IDENTIFICADOS:")
print(f"   {list(top_10)}\n")

# Filtrar vendas apenas do Top 10
vendas_top_10 = vendas_com_categoria[vendas_com_categoria['id_client'].isin(top_10)]

# Contar quantidade por categoria
categorias_count = vendas_top_10.groupby('categoria_normalizada')['qtd'].sum().reset_index()
categorias_count.columns = ['categoria', 'total_itens']
categorias_count = categorias_count.sort_values('total_itens', ascending=False)

print("📊 QUANTIDADE DE ITENS POR CATEGORIA (Top 10):")
print(categorias_count.to_string(index=False))
print()

# Resposta
categoria_resposta = categorias_count.iloc[0]['categoria']
total_itens = categorias_count.iloc[0]['total_itens']

print("=" * 60)
print(f"✅ RESPOSTA QUESTÃO 5.2:")
print(f"   Categoria mais vendida: {categoria_resposta}")
print(f"   Total de itens: {int(total_itens)}")
print("=" * 60)
