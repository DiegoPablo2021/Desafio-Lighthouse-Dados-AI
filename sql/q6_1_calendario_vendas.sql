-- =============================================
-- QUESTÃO 6.1 - DIMENSÃO DE CALENDÁRIO COM VENDAS
-- =============================================
-- Objetivo: Calcular a média de vendas por dia da semana
-- Status: Query validada para PostgreSQL 12+
-- 
-- IMPORTANTE:
-- • Inclui dias sem vendas como R$ 0
-- • Usa EXTRACT(DOW FROM data)
-- • Timezone: America/Sao_Paulo (Brasil)
-- =============================================

WITH dim_calendario AS (
    SELECT 
        data,
        CASE EXTRACT(DOW FROM data)
            WHEN 0 THEN 'Domingo'
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
        END as dia_semana,
        EXTRACT(DOW FROM data)::integer as cod_dia_semana
    FROM (
        SELECT generate_series(
            (SELECT MIN(sale_date::date) FROM vendas_2023_2024),
            (SELECT MAX(sale_date::date) FROM vendas_2023_2024),
            INTERVAL '1 day'
        )::date as data
    ) serie_datas
),

vendas_por_data AS (
    SELECT 
        sale_date::date as data_venda,
        SUM(total) as valor_venda_dia
    FROM vendas_2023_2024
    GROUP BY sale_date::date
),

calendario_com_vendas AS (
    SELECT 
        dc.data,
        dc.dia_semana,
        dc.cod_dia_semana,
        COALESCE(vpd.valor_venda_dia, 0) as valor_venda_diario
    FROM dim_calendario dc
    LEFT JOIN vendas_por_data vpd 
        ON dc.data = vpd.data_venda
),

media_por_dia_semana AS (
    SELECT 
        dia_semana,
        cod_dia_semana,
        COUNT(*) as total_dias_no_periodo,
        COUNT(CASE WHEN valor_venda_diario > 0 THEN 1 END) as dias_com_venda,
        ROUND(SUM(valor_venda_diario)::numeric, 2) as total_vendas,
        ROUND(AVG(valor_venda_diario)::numeric, 2) as media_vendas_diaria
    FROM calendario_com_vendas
    GROUP BY dia_semana, cod_dia_semana
)

SELECT 
    dia_semana,
    cod_dia_semana,
    total_dias_no_periodo,
    dias_com_venda,
    total_vendas,
    media_vendas_diaria
FROM media_por_dia_semana
ORDER BY cod_dia_semana ASC;