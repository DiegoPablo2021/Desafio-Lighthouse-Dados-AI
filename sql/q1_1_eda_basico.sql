-- =============================================
-- QUESTÃO 1.1 - EDA Básico (SQL)
-- =============================================
-- Objetivo: Calcular métricas básicas do dataset vendas_2023_2024
-- Compatível com: PostgreSQL 12+
-- =============================================

-- Parte 1: Visão geral do dataset
SELECT
    COUNT(*)                            AS quantidade_total_linhas,
    6                                   AS quantidade_total_colunas,
    MIN(sale_date::date)                AS data_minima,
    MAX(sale_date::date)                AS data_maxima,
    MAX(sale_date::date) - MIN(sale_date::date) AS intervalo_dias
FROM vendas_2023_2024;

-- Parte 2: Análise de valores numéricos (coluna "total")
SELECT
    MIN(total)                          AS valor_minimo,
    MAX(total)                          AS valor_maximo,
    ROUND(AVG(total)::numeric, 2)       AS valor_medio,
    ROUND(STDDEV(total)::numeric, 2)    AS desvio_padrao,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY total)   AS mediana
FROM vendas_2023_2024;
