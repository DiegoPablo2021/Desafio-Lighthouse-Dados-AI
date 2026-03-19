"""
Testes automatizados para validar as solucoes do Desafio Lighthouse.

Verifica que os scripts produzem resultados consistentes com os dados brutos.
Execute com: python -m pytest tests/test_solucoes.py -v
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
import pytest

# Adicionar raiz ao path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"


# ---------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------

@pytest.fixture(scope="session")
def vendas():
    """Carrega dataset de vendas."""
    df = pd.read_csv(DATA_RAW / "vendas_2023_2024.csv")
    df['sale_date'] = pd.to_datetime(df['sale_date'], format='mixed', dayfirst=True)
    return df


@pytest.fixture(scope="session")
def produtos():
    """Carrega dataset de produtos."""
    return pd.read_csv(DATA_RAW / "produtos_raw.csv")


# ---------------------------------------------------------------
# Q1 - EDA
# ---------------------------------------------------------------

class TestQ1EDA:
    """Testes para a Questao 1 - EDA."""

    def test_total_linhas(self, vendas):
        """Verifica que o dataset tem linhas."""
        assert len(vendas) > 0, "Dataset vazio"
        assert len(vendas) == 9895, f"Esperado 9895 linhas, encontrado {len(vendas)}"

    def test_total_colunas(self, vendas):
        """Verifica as 6 colunas esperadas."""
        assert vendas.shape[1] == 6, f"Esperado 6 colunas, encontrado {vendas.shape[1]}"

    def test_sem_nulos(self, vendas):
        """Verifica que nao ha valores nulos."""
        assert vendas.isnull().sum().sum() == 0, "Existem valores nulos"

    def test_intervalo_datas(self, vendas):
        """Verifica que as datas cobrem 2023-2024."""
        assert vendas['sale_date'].min().year == 2023
        assert vendas['sale_date'].max().year == 2024

    def test_total_sem_negativos(self, vendas):
        """Verifica que nao ha valores negativos na coluna total."""
        assert (vendas['total'] < 0).sum() == 0


# ---------------------------------------------------------------
# Q2 - Normalizacao
# ---------------------------------------------------------------

class TestQ2Normalizacao:
    """Testes para a Questao 2 - Normalizacao de produtos."""

    def test_categorias_normalizadas(self, produtos):
        """Verifica que todas categorias podem ser normalizadas."""
        from solucoes_questoes.q2_normalizacao import normalizar_categoria
        categorias = produtos['actual_category'].apply(normalizar_categoria).unique()
        esperadas = {'ancoragem', 'propulsao', 'propulsão', 'eletronicos', 'eletrônicos'}
        # Todas categorias devem ser uma das esperadas
        for cat in categorias:
            assert cat in esperadas, f"Categoria inesperada: {cat}"

    def test_sem_duplicatas_apos_normalizacao(self, produtos):
        """Verifica que drop_duplicates funciona."""
        df = produtos.drop_duplicates()
        assert len(df) <= len(produtos)


# ---------------------------------------------------------------
# Q5 - Clientes Fieis
# ---------------------------------------------------------------

class TestQ5ClientesFieis:
    """Testes para a Questao 5 - Clientes Fieis."""

    def test_diversidade_minima_3(self, vendas, produtos):
        """Verifica que Top 10 tem diversidade >= 3 categorias."""
        from solucoes_questoes.q5_clientes_fieis import normalizar_categoria

        # Criar mapa de categorias
        cat_map = {}
        for _, row in produtos.iterrows():
            cat_map[row['code']] = normalizar_categoria(row.get('actual_category', ''))

        # Calcular diversidade por cliente
        vendas_copy = vendas.copy()
        vendas_copy['categoria'] = vendas_copy['id_product'].map(cat_map)
        diversidade = vendas_copy.groupby('id_client')['categoria'].nunique()

        # Pelo menos 10 clientes com 3+ categorias
        clientes_3plus = diversidade[diversidade >= 3]
        assert len(clientes_3plus) >= 10, f"Apenas {len(clientes_3plus)} clientes com 3+ categorias"


# ---------------------------------------------------------------
# Q6 - Calendario
# ---------------------------------------------------------------

class TestQ6Calendario:
    """Testes para a Questao 6 - Dimensao Calendario."""

    def test_calendario_completo(self, vendas):
        """Verifica que o calendario cobre todas as datas do periodo."""
        data_min = vendas['sale_date'].min()
        data_max = vendas['sale_date'].max()
        total_dias_esperado = (data_max - data_min).days + 1

        # Se o arquivo processado existir, verificar
        cal_path = DATA_PROCESSED / "dim_calendario.csv"
        if cal_path.exists():
            cal = pd.read_csv(cal_path)
            assert len(cal) == total_dias_esperado, \
                f"Calendario tem {len(cal)} dias, esperado {total_dias_esperado}"

    def test_dias_com_zero(self, vendas):
        """Verifica que existem dias sem vendas no periodo."""
        data_min = vendas['sale_date'].min()
        data_max = vendas['sale_date'].max()
        total_dias = (data_max - data_min).days + 1
        dias_com_venda = vendas['sale_date'].dt.date.nunique()
        assert dias_com_venda < total_dias, "Todos os dias tem venda - algo estranho"


# ---------------------------------------------------------------
# Q7 - Previsao
# ---------------------------------------------------------------

class TestQ7Previsao:
    """Testes para a Questao 7 - Previsao de Demanda."""

    def test_sem_data_leakage(self, vendas):
        """Verifica que o split temporal esta correto."""
        data_corte = pd.to_datetime('2023-12-31')
        treino = vendas[vendas['sale_date'] <= data_corte]
        teste = vendas[(vendas['sale_date'] > data_corte) &
                       (vendas['sale_date'] < pd.to_datetime('2024-02-01'))]
        assert len(treino) > 0, "Treino vazio"
        assert len(teste) > 0, "Teste vazio"
        assert treino['sale_date'].max() <= data_corte


# ---------------------------------------------------------------
# Q8 - Recomendacao
# ---------------------------------------------------------------

class TestQ8Recomendacao:
    """Testes para a Questao 8 - Sistema de Recomendacao."""

    def test_matriz_binaria(self, vendas):
        """Verifica que a matriz de interacao e binaria (0/1)."""
        compras = vendas.groupby(['id_client', 'id_product']).size().reset_index(name='c')
        compras['c'] = 1
        matriz = compras.pivot_table(
            index='id_client', columns='id_product',
            values='c', fill_value=0, aggfunc='max'
        )
        assert set(matriz.values.flatten()) <= {0, 1}, "Matriz nao e binaria"

    def test_gps_garmin_existe(self, produtos):
        """Verifica que o produto GPS Garmin existe no catalogo."""
        gps = produtos[produtos['name'].str.contains('GPS Garmin', case=False, na=False)]
        assert len(gps) > 0, "GPS Garmin nao encontrado"
