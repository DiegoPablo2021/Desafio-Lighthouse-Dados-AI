-- =============================================
-- QUESTÃO 4.1 - Análise de Prejuízos por Produto (SQL)
-- =============================================
-- Objetivo: Calcular custo em BRL, agregação por produto com
-- receita total, prejuízo total e percentual de perda.
--
-- Premissas:
--   • custo_brl = custo_usd × taxa_cambio_dia × quantidade
--   • Prejuízo = quando custo_brl > valor de venda
--   • Receita total = soma de TODAS as vendas por produto
--   • Percentual = prejuízo_total / receita_total
--
-- Requer tabelas:
--   • vendas_2023_2024 (id, id_client, id_product, qtd, total, sale_date)
--   • custos_importacao (product_id, start_date, usd_price)
--   • cambio_diario (data, taxa_venda)  ← taxa PTAX do BCB
--
-- Compatível com: PostgreSQL 12+
-- =============================================

WITH custo_vigente AS (
    -- Para cada produto e data de venda, encontrar o custo USD mais recente
    SELECT DISTINCT ON (v.id)
        v.id              AS venda_id,
        v.id_product,
        v.qtd,
        v.total           AS receita_brl,
        v.sale_date::date AS data_venda,
        c.usd_price       AS custo_usd,
        c.start_date      AS data_custo
    FROM vendas_2023_2024 v
    JOIN custos_importacao c ON v.id_product = c.product_id
                            AND c.start_date::date <= v.sale_date::date
    ORDER BY v.id, c.start_date::date DESC
),

calculo_prejuizo AS (
    -- Calcular custo em BRL usando câmbio do dia
    SELECT
        cv.venda_id,
        cv.id_product,
        cv.qtd,
        cv.receita_brl,
        cv.custo_usd,
        cd.taxa_venda                           AS taxa_cambio,
        cv.custo_usd * cd.taxa_venda * cv.qtd   AS custo_total_brl,
        GREATEST(
            0,
            cv.custo_usd * cd.taxa_venda * cv.qtd - cv.receita_brl
        )                                        AS prejuizo_transacao
    FROM custo_vigente cv
    LEFT JOIN cambio_diario cd ON cd.data = cv.data_venda
)

SELECT
    id_product,
    ROUND(SUM(receita_brl)::numeric, 2)                    AS receita_total_brl,
    ROUND(SUM(prejuizo_transacao)::numeric, 2)              AS prejuizo_total_brl,
    ROUND(
        (SUM(prejuizo_transacao) / NULLIF(SUM(receita_brl), 0) * 100)::numeric,
        2
    )                                                       AS percentual_perda
FROM calculo_prejuizo
GROUP BY id_product
HAVING SUM(prejuizo_transacao) > 0
ORDER BY prejuizo_total_brl DESC;