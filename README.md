# Desafio Lighthouse - Dados & AI

## Visão Geral

Análise completa dos dados da **LH Nautical** (2023-2024) com foco em **EDA, tratamento de dados, modelagem preditiva e sistemas de recomendação**. O projeto implementa uma pipeline end-to-end de Data Science orientada pelos princípios de organização e clareza, contendo soluções para as 8 questões do desafio (Q1-Q8).

Neste repositório, você encontrará a **resolução modularizada** de cada questão (arquivos `.py` e `.sql`) que deve ser submetida na plataforma de respostas, além de um **Relatório Executivo** detalhado e um **Notebook Consolidado** contendo os insights e visualizações unificadas.

---

## Objetivos e Entregáveis

| Questão | Tema | Entregáveis |
|---------|------|-------------|
| **Q1** | Exploração e Diagnóstico (EDA) | Python + SQL + Interpretação |
| **Q2** | Normalização de Produtos | Python |
| **Q3** | Custos de Importação (JSON → CSV) | Python |
| **Q4** | Análise de Prejuízos (câmbio BCB) | Python + SQL + Interpretação |
| **Q5** | Clientes Fiéis (Top 10 + Categorias) | Python + SQL + Interpretação |
| **Q6** | Dimensão Calendário (dias sem venda) | Python + SQL + Interpretação |
| **Q7** | Previsão de Demanda (Média Móvel 7d) | Python + Interpretação |
| **Q8** | Sistema de Recomendação (Cosseno) | Python + Interpretação |

---

## Estrutura do Projeto

```
Desafio-Lighthouse-Dados-AI/
│
├── data/
│   ├── raw/                        # Dados originais (fornecidos)
│   │   ├── custos_importacao.json
│   │   ├── produtos_raw.csv
│   │   └── vendas_2023_2024.csv
│   │
│   └── processed/                  # Dados processados (gerados pelos scripts)
│       ├── custos_importacao.csv
│       ├── dim_calendario.csv
│       ├── previsao_motor_popa_janeiro_2024.csv
│       ├── produtos_normalizado.csv
│       └── recomendacoes_gps_garmin.csv
│
├── solucoes_questoes/           # Scripts Python com respostas submissíveis
│   ├── q1_exploracao_diagnostico.py    # Q1: EDA + Q1.3 Interpretação
│   ├── q2_normalizacao.py              # Q2: Padronização de categorias
│   ├── q3_custos.py                    # Q3: JSON → CSV
│   ├── q4_prejuizo.py                  # Q4: Prejuízos + câmbio
│   ├── q5_clientes_fieis.py            # Q5: Top 10 + Q5.3 Explicação
│   ├── q5_2_categoria_mais_vendida.py  # Q5.2: Categoria mais vendida
│   ├── q6_calendario.py                # Q6: Calendário completo + Q6.3
│   ├── q7_1_modelo_baseline.py         # Q7: MA7 + Q7.2/Q7.3
│   └── q8_1_recomendacao.py            # Q8: Cosseno + Q8.2/Q8.3
│
├── sql/                         # Queries SQL (PostgreSQL) para submissão
│   ├── q1_1_eda_basico.sql             # Q1.1: métricas EDA
│   ├── q4_prejuizo_produtos.sql        # Q4.1: prejuízos com câmbio
│   ├── q5_2_categoria_mais_vendida.sql # Q5.1: clientes fiéis + categorias
│   └── q6_1_calendario_vendas.sql      # Q6.1: dimensão calendário
│
├── notebooks/                   # Análises exploratórias (Jupyter)
│   ├── 06_relatorio_consolidado.ipynb  # ENTREGA PRINCIPAL
│   └── drafts/                         # Notebooks exploratórios arquivados
│       ├── 01_eda_vendas.ipynb
│       ├── 02_tratamento_e_features.ipynb
│       ├── 03_modelo_previsao_e_insights.ipynb
│       ├── 04_modelo_previsao.ipynb
│       └── 05_recomendacao.ipynb
│
├── src/                         # Módulos reutilizáveis
│   ├── data/
│   ├── features/
│   ├── models/
│   └── utils.py
│
├── tests/                       # Testes de unidade
│   └── test_solucoes.py
│
├── README.md                       # Este arquivo referencial
├── RELATORIO_EXECUTIVO.md          # Relatório voltado para tomada de decisões gerenciais
└── requirements.txt                # Dependências Python
```

---

## Como Executar

### 1. Configurar Ambiente

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows - PowerShell)
.\.venv\Scripts\Activate.ps1

# Ativar (Linux/macOS)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar Scripts (Respostas individuais)
Os códigos que deverão ser submetidos no portal da prova encontram-se em `solucoes_questoes/` (Python) e `sql/` (SQL). Você pode processar as análises caso precise inspecionar os resultados:

```bash
python solucoes_questoes/q1_exploracao_diagnostico.py
python solucoes_questoes/q2_normalizacao.py
# ... e assim por diante para todas as questões.
```

### 3. Notebook Consolidado (Entrega Analítica Final)
Para a análise em profundidade, recomenda-se iniciar o Jupyter Server e ler/executar o notebook final da entrega, onde todas as interações e cruzamentos de dados foram gerados graficamente.
O arquivo principal é:
`notebooks/06_relatorio_consolidado.ipynb`

### 4. Executar SQL (PostgreSQL)

```bash
psql -d lighthouse -U postgres

# Dentro do psql:
\i sql/q1_1_eda_basico.sql
\i sql/q4_prejuizo_produtos.sql
\i sql/q5_2_categoria_mais_vendida.sql
\i sql/q6_1_calendario_vendas.sql
```

---

## Dependências Relevantes

| Biblioteca | Versão Mín. | Uso |
|------------|-------------|-----|
| pandas | 2.2.0 | Manipulação de dados |
| numpy | 1.26.0 | Operações numéricas |
| scikit-learn | 1.4.0 | Similaridade de cosseno |
| requests | 2.31.0 | API (câmbio BCB) |
| jupyter | 1.0.0 | Notebook interativo (`06_relatorio_consolidado.ipynb`) |

---

## Autor

**Diego Pablo**

- **LinkedIn**: [diego-pablo](https://www.linkedin.com/in/diego-pablo/)
- **Portfolio**: [diego-pablo.vercel.app](https://diego-pablo.vercel.app/)
- **GitHub**: [DiegoPablo2021](https://github.com/DiegoPablo2021)

---

**Desafio Lighthouse - Indicium**  
**Última atualização**: Março de 2026