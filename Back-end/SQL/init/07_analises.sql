
WITH limites AS (
  SELECT
    MIN(ano * 10 + trimestre) AS periodo_inicial,
    MAX(ano * 10 + trimestre) AS periodo_final
  FROM app.despesas_consolidadas
),
primeiro_ultimo AS (
  SELECT
    d.operadora_id,
    SUM(CASE
          WHEN (d.ano * 10 + d.trimestre) = l.periodo_inicial
          THEN d.valor_despesas
          ELSE 0
        END) AS valor_inicial,
    SUM(CASE
          WHEN (d.ano * 10 + d.trimestre) = l.periodo_final
          THEN d.valor_despesas
          ELSE 0
        END) AS valor_final
  FROM app.despesas_consolidadas d
  CROSS JOIN limites l
  GROUP BY d.operadora_id
),
crescimento AS (
  SELECT
    operadora_id,
    valor_inicial,
    valor_final,
    ((valor_final - valor_inicial) / valor_inicial) * 100.0
      AS crescimento_percentual
  FROM primeiro_ultimo
  WHERE valor_inicial > 0
    AND valor_final > 0
)
SELECT
  o.razao_social,
  c.valor_inicial,
  c.valor_final,
  ROUND(c.crescimento_percentual, 2) AS crescimento_percentual
FROM crescimento c
JOIN app.operadoras o
  ON o.operadora_id = c.operadora_id
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- ------------------------------------------------------------
-- Query 2
-- Distribuição de despesas por UF
-- Top 5 UFs com maiores despesas totais
-- + média de despesas por operadora em cada UF
--
-- Fonte: app.despesas_agregadas
-- ------------------------------------------------------------

SELECT
  uf,
  SUM(total_despesas) AS total_despesas_uf,
  COUNT(DISTINCT COALESCE(operadora_id::text, razao_social)) AS qtd_operadoras_uf,
  ROUND(AVG(total_despesas), 2) AS media_por_operadora_uf
FROM app.despesas_agregadas
WHERE uf IS NOT NULL
  AND total_despesas IS NOT NULL
GROUP BY uf
ORDER BY total_despesas_uf DESC
LIMIT 5;

-- CTES

WITH trimestres AS (
  SELECT DISTINCT ano, trimestre
  FROM app.despesas_consolidadas
  ORDER BY ano, trimestre
  LIMIT 3
),
operadora_tri AS (
  SELECT
    d.operadora_id,
    d.ano,
    d.trimestre,
    SUM(d.valor_despesas) AS valor_operadora
  FROM app.despesas_consolidadas d
  JOIN trimestres t
    ON t.ano = d.ano
   AND t.trimestre = d.trimestre
  GROUP BY d.operadora_id, d.ano, d.trimestre
),
media_tri AS (
  SELECT
    ano,
    trimestre,
    AVG(valor_operadora) AS media_trimestre
  FROM operadora_tri
  GROUP BY ano, trimestre
),
acima_media AS (
  SELECT
    o.operadora_id,
    COUNT(*) FILTER (
      WHERE o.valor_operadora > m.media_trimestre
    ) AS qtd_trimestres_acima
  FROM operadora_tri o
  JOIN media_tri m
    ON m.ano = o.ano
   AND m.trimestre = o.trimestre
  GROUP BY o.operadora_id
)
SELECT
  COUNT(*) AS operadoras_acima_em_pelo_menos_2_trimestres
FROM acima_media
WHERE qtd_trimestres_acima >= 2;
