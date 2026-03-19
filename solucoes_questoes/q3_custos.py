"""
Q3: Transformação de Custos de Importação

Carrega arquivo JSON custos_importacao.json e gera novo arquivo CSV
organizando os dados de histórico de preços.
"""

import json
import csv
from pathlib import Path


def main():
    """Lê JSON de custos e exporta para CSV."""
    
    # Carregando arquivo JSON
    json_file = Path("data/raw/custos_importacao.json")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        exit(1)

    print(f"Arquivo JSON carregado com {len(data)} produtos\n")

    # Processando os dados: expandindo histórico
    linhas_csv = []
    
    for produto in data:
        product_id = produto.get('product_id')
        product_name = produto.get('product_name')
        category = produto.get('category')
        
        # Se houver histórico, criar uma linha por entrada
        if 'historic_data' in produto:
            for entrada in produto['historic_data']:
                start_date = entrada.get('start_date')
                usd_price = entrada.get('usd_price')
                
                linhas_csv.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'category': category,
                    'start_date': start_date,
                    'usd_price': usd_price
                })

    print(f"Total de registros no histórico: {len(linhas_csv)}")
    print(f"Estrutura esperada: product_id, product_name, category, start_date, usd_price\n")

    # Salvando em CSV
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "custos_importacao.csv"
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if linhas_csv:
                fieldnames = ['product_id', 'product_name', 'category', 'start_date', 'usd_price']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(linhas_csv)
        
        print(f"Arquivo CSV salvo em: {output_file}")
        
    except Exception as e:
        print(f"Erro ao salvar CSV: {e}")
        exit(1)


if __name__ == "__main__":
    main()
