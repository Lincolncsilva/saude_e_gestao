-- =========================
-- 2) RAW -> APP (operadoras)
-- =========================

-- Rejeita linhas sem identificador mínimo
INSERT INTO audit.rejeitos_importacao (origem_arquivo, motivo, payload)
SELECT
  'Relatorio_cadop.csv',
  'registro_operadora ou cnpj ausente',
  to_jsonb(r)
FROM raw.stg_operadoras_ans r
WHERE NULLIF(trim(r.registro_operadora),'') IS NULL
   OR NULLIF(regexp_replace(r.cnpj, '\D', '', 'g'),'') IS NULL;

-- Insere/atualiza válidos
INSERT INTO app.operadoras (
  registro_operadora, cnpj, razao_social, nome_fantasia, modalidade,
  logradouro, numero, complemento, bairro, cidade, uf, cep,
  ddd, telefone, fax, endereco_eletronico,
  representante, cargo_representante, regiao_de_comercializacao, data_registro_ans
)
SELECT
  trim(registro_operadora),
  regexp_replace(cnpj, '\D', '', 'g'),
  NULLIF(trim(razao_social),'') ,
  NULLIF(trim(nome_fantasia),''),
  NULLIF(trim(modalidade),''),
  NULLIF(trim(logradouro),''),
  NULLIF(trim(numero),''),
  NULLIF(trim(complemento),''),
  NULLIF(trim(bairro),''),
  NULLIF(trim(cidade),''),
  CASE WHEN length(trim(uf))=2 THEN upper(trim(uf))::char(2) ELSE NULL END,
  NULLIF(regexp_replace(cep, '\D', '', 'g'),''),
  NULLIF(trim(ddd),''),
  NULLIF(trim(telefone),''),
  NULLIF(trim(fax),''),
  NULLIF(trim(endereco_eletronico),''),
  NULLIF(trim(representante),''),
  NULLIF(trim(cargo_representante),''),
  NULLIF(trim(regiao_de_comercializacao),'')::smallint,
  CASE
    WHEN data_registro_ans ~ '^\d{4}-\d{2}-\d{2}$' THEN data_registro_ans::date
    ELSE NULL
  END
FROM raw.stg_operadoras_ans
WHERE NULLIF(trim(registro_operadora),'') IS NOT NULL
  AND NULLIF(regexp_replace(cnpj, '\D', '', 'g'),'') IS NOT NULL
ON CONFLICT (registro_operadora)
DO UPDATE SET
  cnpj = EXCLUDED.cnpj,
  razao_social = EXCLUDED.razao_social,
  nome_fantasia = EXCLUDED.nome_fantasia,
  modalidade = EXCLUDED.modalidade,
  logradouro = EXCLUDED.logradouro,
  numero = EXCLUDED.numero,
  complemento = EXCLUDED.complemento,
  bairro = EXCLUDED.bairro,
  cidade = EXCLUDED.cidade,
  uf = EXCLUDED.uf,
  cep = EXCLUDED.cep,
  ddd = EXCLUDED.ddd,
  telefone = EXCLUDED.telefone,
  fax = EXCLUDED.fax,
  endereco_eletronico = EXCLUDED.endereco_eletronico,
  representante = EXCLUDED.representante,
  cargo_representante = EXCLUDED.cargo_representante,
  regiao_de_comercializacao = EXCLUDED.regiao_de_comercializacao,
  data_registro_ans = EXCLUDED.data_registro_ans;

-- =========================
-- 3) RAW -> APP (despesas consolidadas)
--    Tratamento: consolida duplicados (SUM) e rejeita linhas inválidas
-- =========================

WITH cleaned AS (
  SELECT
    NULLIF(regexp_replace(cnpj, '\D', '', 'g'), '') AS cnpj_digits,
    NULLIF(trim(trimestre),'')::int AS tri_i,
    NULLIF(trim(ano),'')::int AS ano_i,
    CASE
      WHEN valordespesas IS NULL OR trim(valordespesas) = '' THEN NULL
      ELSE NULLIF(regexp_replace(valordespesas, '[^0-9\.\-]', '', 'g'),'')::numeric
    END AS valor_num,
    cnpj_valido, valor_valido, rs_valida,
    to_jsonb(s) AS payload
  FROM raw.stg_consolidado_despesas s
),
rejected AS (
  SELECT *
  FROM cleaned
  WHERE cnpj_digits IS NULL
     OR ano_i IS NULL OR ano_i NOT BETWEEN 2000 AND 2100
     OR tri_i IS NULL OR tri_i NOT BETWEEN 1 AND 4
     OR valor_num IS NULL OR valor_num < 0
     OR valor_valido <> 'True'
     OR cnpj_valido <> 'True'
)
INSERT INTO audit.rejeitos_importacao (origem_arquivo, tabela_destino, motivo, payload)
SELECT
  'consolidado_despesas.csv',
  'app.despesas_consolidadas',
  'cnpj/periodo/valor invalido ou flags falsas (cnpj_valido/valor_valido)',
  payload
FROM rejected;


-- Inserção (agregando duplicados por operadora/período)
INSERT INTO app.despesas_consolidadas (operadora_id, ano, trimestre, valor_despesas)
SELECT
  o.operadora_id,
  c.ano_i::smallint,
  c.tri_i::smallint,
  SUM(c.valor_num)::numeric(18,2) AS valor_total_periodo
FROM (
  SELECT
    NULLIF(regexp_replace(cnpj, '\D', '', 'g'), '') AS cnpj_digits,
    NULLIF(trim(trimestre),'')::int AS tri_i,
    NULLIF(trim(ano),'')::int AS ano_i,
    NULLIF(regexp_replace(valordespesas, '[^0-9\.\-]', '', 'g'),'')::numeric AS valor_num,
    cnpj_valido, valor_valido
  FROM raw.stg_consolidado_despesas
) c
JOIN app.operadoras o ON o.cnpj = c.cnpj_digits
WHERE c.cnpj_digits IS NOT NULL
  AND c.ano_i BETWEEN 2000 AND 2100
  AND c.tri_i BETWEEN 1 AND 4
  AND c.valor_num IS NOT NULL
  AND c.valor_num >= 0
  AND c.cnpj_valido = 'True'
  AND c.valor_valido = 'True'
GROUP BY o.operadora_id, c.ano_i, c.tri_i
ON CONFLICT (operadora_id, ano, trimestre)
DO UPDATE SET
  valor_despesas = EXCLUDED.valor_despesas,
  loaded_at = now();

-- Map de razao_social -> operadora_id (heurística por igualdade case-insensitive)
WITH map_operadoras AS (
  SELECT
    lower(trim(razao_social)) AS key_rs,
    MIN(operadora_id) AS operadora_id
  FROM app.operadoras
  GROUP BY lower(trim(razao_social))
)
INSERT INTO app.despesas_agregadas (
  operadora_id, razao_social, uf, total_despesas, media_trimestral, desvio_padrao_despesas
)
SELECT
  m.operadora_id,
  NULLIF(trim(s.razaosocial),'') AS razao_social,
  CASE WHEN length(trim(s.uf))=2 THEN upper(trim(s.uf))::char(2) ELSE NULL END,
  NULLIF(regexp_replace(s.total_despesas, '[^0-9\.\-]', '', 'g'),'')::numeric,
  NULLIF(regexp_replace(s.media_trimestral, '[^0-9\.\-]', '', 'g'),'')::numeric,
  NULLIF(regexp_replace(s.desvio_padrao_despesas, '[^0-9\.\-]', '', 'g'),'')::numeric
FROM raw.stg_despesas_agregadas s
LEFT JOIN map_operadoras m ON m.key_rs = lower(trim(s.razaosocial))
WHERE NULLIF(trim(s.razaosocial),'') IS NOT NULL;

-- =========================
-- 5) META (evidência simples)
-- =========================

INSERT INTO meta.cargas (origem_arquivo, linhas_lidas, linhas_rejeitadas)
SELECT 'Relatorio_cadop.csv', COUNT(*), (SELECT COUNT(*) FROM audit.rejeitos_importacao WHERE origem_arquivo='Relatorio_cadop.csv')
FROM raw.stg_operadoras_ans;

INSERT INTO meta.cargas (origem_arquivo, linhas_lidas, linhas_rejeitadas)
SELECT 'consolidado_despesas.csv', COUNT(*), (SELECT COUNT(*) FROM audit.rejeitos_importacao WHERE origem_arquivo='consolidado_despesas.csv')
FROM raw.stg_consolidado_despesas;

INSERT INTO meta.cargas (origem_arquivo, linhas_lidas, linhas_rejeitadas)
SELECT 'despesas_agregadas.csv', COUNT(*), (SELECT COUNT(*) FROM audit.rejeitos_importacao WHERE origem_arquivo='despesas_agregadas.csv')
FROM raw.stg_despesas_agregadas;
