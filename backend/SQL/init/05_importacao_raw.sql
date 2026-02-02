-- =========================
-- 1) COPY -> RAW (UTF-8)
-- =========================

TRUNCATE raw.stg_operadoras_ans;

-- CSV da ANS usa ';' e aspas. Pode ter quebras de linha dentro de campos (Postgres COPY suporta em CSV).
COPY raw.stg_operadoras_ans
FROM '/data/references/Relatorio_cadop.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ';', QUOTE '"', ENCODING 'UTF8');

TRUNCATE raw.stg_consolidado_despesas;
COPY raw.stg_consolidado_despesas
FROM '/data/processed/2025/consolidado_despesas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', ENCODING 'UTF8');

TRUNCATE raw.stg_despesas_agregadas;
COPY raw.stg_despesas_agregadas
FROM '/data/processed/despesas_agregadas.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', QUOTE '"', ENCODING 'UTF8');

