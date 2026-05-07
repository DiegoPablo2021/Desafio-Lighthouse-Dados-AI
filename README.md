# Lighthouse Dados AI

![Python](https://img.shields.io/badge/Python-Data%20Science-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Analytical%20Queries-336791?logo=postgresql&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-Recommendation-F7931E?logo=scikit-learn&logoColor=white)

End-to-end data science challenge built around exploratory analysis, predictive reasoning, and recommendation logic for the LH Nautical business context. The project is organized to show analytical depth, modular delivery, and decision-oriented interpretation instead of isolated notebook output.

## Executive Summary

The challenge covers eight analytical questions across exploration, cleaning, forecasting, and recommendation. This repository packages those answers as a cleaner portfolio artifact with:

- modular Python scripts for each deliverable
- SQL queries for the required analytical questions
- a consolidated notebook for business-facing storytelling
- reusable `src/` modules for data, features, and models
- unit tests for the solution layer

## Business Problem

The objective was to examine transactional and product data, uncover meaningful patterns, and generate outputs that support real commercial reasoning, including:

- product normalization
- loss analysis
- loyal-customer interpretation
- calendar and demand analysis
- recommendation logic

The value of the case is not any single chart or model. It is the ability to move from raw data to structured business interpretation.

## Solution Overview

### 1. Exploration And Data Diagnosis

The project starts by profiling the quality, structure, and analytical signal of the source data before introducing transformations.

### 2. Data Preparation

Feature and cleaning logic standardize products, costs, and supporting analytical tables required for downstream interpretation.

### 3. Predictive And Recommendation Logic

The repository includes forecasting and similarity-based recommendation workflows to show broader data science coverage.

### 4. Business-Facing Delivery

The final notebook consolidates the work into a more coherent narrative for review and presentation.

## Repository Structure

```text
Desafio-Lighthouse-Dados-AI/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 06_relatorio_consolidado.ipynb
│   └── drafts/
├── solucoes_questoes/
├── sql/
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── utils.py
├── tests/
├── README.md
└── requirements.txt
```

## Deliverables

- `solucoes_questoes/`: Python answers for the challenge questions
- `sql/`: SQL outputs required by the exercise
- `notebooks/06_relatorio_consolidado.ipynb`: consolidated analytical narrative
- `data/processed/`: generated outputs used in the analysis

## Technical Stack

- Python
- pandas / numpy
- scikit-learn
- SQL
- Jupyter

## How To Run

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the solution scripts

```bash
python solucoes_questoes/q1_exploracao_diagnostico.py
python solucoes_questoes/q2_normalizacao.py
python solucoes_questoes/q3_custos.py
python solucoes_questoes/q4_prejuizo.py
python solucoes_questoes/q5_clientes_fieis.py
python solucoes_questoes/q6_calendario.py
python solucoes_questoes/q7_1_modelo_baseline.py
python solucoes_questoes/q8_1_recomendacao.py
```

### 4. Open the consolidated notebook

```bash
jupyter notebook notebooks/06_relatorio_consolidado.ipynb
```

### 5. Run tests

```bash
pytest tests/test_solucoes.py
```

## Portfolio Relevance

This project is useful in a portfolio because it demonstrates a balanced data science profile: data understanding, feature reasoning, predictive thinking, recommendation framing, and the ability to communicate analytical complexity in a way that is easier for business stakeholders to consume.

## Author

**Diego Pablo**

- Portfolio: [diego-pablo.vercel.app](https://diego-pablo.vercel.app/)
- LinkedIn: [linkedin.com/in/diego-pablo](https://www.linkedin.com/in/diego-pablo/)
