-- =============================================
-- QUESTÃO 5.1 - Clientes Fiéis (SQL)
-- =============================================
-- Objetivo:
--   1. Calcular Ticket Médio e Diversidade de categorias por cliente
--   2. Filtrar Top 10 clientes com maior Ticket Médio E diversidade >= 3 categorias
--   3. Identificar a categoria mais vendida (qtd total) entre os Top 10
--
-- Premissas:
--   • Faturamento Total = SUM(total) por cliente
--   • Frequência = COUNT de transações por cliente
--   • Ticket Médio = Faturamento Total / Frequência
--   • Diversidade = categorias distintas (após normalização)
--   • Desempate: id_client ASC
--
-- Requer tabelas:
--   • vendas_2023_2024 (id, id_client, id_product, qtd, total, sale_date)
--   • produtos (code, actual_category) ← categorias normalizadas
--
-- Compatível com: PostgreSQL 12+
-- =============================================

-- Primeiro: normalizar categorias via CASE
WITH produtos_norm AS (
    SELECT
        code,
        CASE
            WHEN LOWER(actual_category) SIMILAR TO '%(ancor|encor)%' THEN 'ancoragem'
            WHEN LOWER(actual_category) SIMILAR TO '%(eletr|electron)%' THEN 'eletrônicos'
            WHEN LOWER(actual_category) SIMILAR TO '%(prop|propul)%' THEN 'propulsão'
            ELSE LOWER(actual_category)
        END AS categoria_normalizada
    FROM produtos
),

-- Calcular métricas por cliente
metricas_cliente AS (
    SELECT
        v.id_client,
        SUM(v.total)                                            AS faturamento_total,
        COUNT(*)                                                AS frequencia,
        ROUND((SUM(v.total) / NULLIF(COUNT(*), 0))::numeric, 2) AS ticket_medio,
        COUNT(DISTINCT p.categoria_normalizada)                  AS diversidade_categorias
    FROM vendas_2023_2024 v
    JOIN produtos_norm p ON v.id_product = p.code
    GROUP BY v.id_client
),

-- Filtrar Top 10: diversidade >= 3, ordenar por ticket médio DESC, id ASC
top_10 AS (
    SELECT id_client
    FROM metricas_cliente
    WHERE diversidade_categorias >= 3
    ORDER BY ticket_medio DESC, id_client ASC
    LIMIT 10
)

-- Resultado 1: Dados dos Top 10 clientes
SELECT
    mc.id_client,
    mc.faturamento_total,
    mc.frequencia,
    mc.ticket_medio,
    mc.diversidade_categorias
FROM metricas_cliente mc
WHERE mc.id_client IN (SELECT id_client FROM top_10)
ORDER BY mc.ticket_medio DESC, mc.id_client ASC;

-- =============================================
-- Resultado 2: Categoria mais vendida (qtd) pelos Top 10
-- =============================================
WITH produtos_norm AS (
    SELECT
        code,
        CASE
            WHEN LOWER(actual_category) SIMILAR TO '%(ancor|encor)%' THEN 'ancoragem'
            WHEN LOWER(actual_category) SIMILAR TO '%(eletr|electron)%' THEN 'eletrônicos'
            WHEN LOWER(actual_category) SIMILAR TO '%(prop|propul)%' THEN 'propulsão'
            ELSE LOWER(actual_category)
        END AS categoria_normalizada
    FROM produtos
),

metricas_cliente AS (
    SELECT
        v.id_client,
        ROUND((SUM(v.total) / NULLIF(COUNT(*), 0))::numeric, 2) AS ticket_medio,
        COUNT(DISTINCT p.categoria_normalizada) AS diversidade_categorias
    FROM vendas_2023_2024 v
    JOIN produtos_norm p ON v.id_product = p.code
    GROUP BY v.id_client
),

top_10 AS (
    SELECT id_client
    FROM metricas_cliente
    WHERE diversidade_categorias >= 3
    ORDER BY ticket_medio DESC, id_client ASC
    LIMIT 10
)

SELECT
    p.categoria_normalizada AS categoria,
    SUM(v.qtd) AS total_itens
FROM vendas_2023_2024 v
JOIN produtos_norm p ON v.id_product = p.code
WHERE v.id_client IN (SELECT id_client FROM top_10)
GROUP BY p.categoria_normalizada
ORDER BY total_itens DESC
LIMIT 1;