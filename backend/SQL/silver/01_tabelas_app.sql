-- ============================================================
-- 1) DDL - APP (SILVER + GOLD)
-- ============================================================

-- Alteração: O script de importação chama "app.operadoras", 
-- mas o DDL chamava "app.operadoras_ans". Padronizei para "app.operadoras".

DROP TABLE IF EXISTS app.operadoras CASCADE;

CREATE TABLE app.operadoras (
  operadora_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

  registro_operadora varchar(20) NOT NULL UNIQUE,
  cnpj               varchar(14) NOT NULL UNIQUE,

  razao_social       text NOT NULL,
  nome_fantasia      text,
  modalidade         text,

  logradouro         text,
  numero             text,
  complemento        text,
  bairro             text,
  cidade             text,
  uf                 char(2),
  cep                varchar(8),

  ddd                varchar(3),
  telefone           varchar(30),
  fax                varchar(30),
  endereco_eletronico text,

  representante      text,
  cargo_representante text,

  regiao_de_comercializacao smallint,
  data_registro_ans  date,

  created_at         timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT operadoras_uf_chk
    CHECK (uf IS NULL OR uf ~ '^[A-Z]{2}$'),

  CONSTRAINT operadoras_cnpj_chk
    CHECK (cnpj ~ '^[0-9]{14}$')
);

-- Indexação para performance nos JOINs e buscas
CREATE INDEX operadoras_uf_idx ON app.operadoras (uf);
CREATE INDEX operadoras_razao_idx ON app.operadoras USING btree (razao_social);
CREATE INDEX IF NOT EXISTS despesas_operadora_idx ON app.despesa_consolidada (operadora_id);


-- =========================
-- FACT: despesas_consolidadas
-- =========================
DROP TABLE IF EXISTS app.despesas_consolidadas;

CREATE TABLE app.despesas_consolidadas (
  operadora_id  bigint NOT NULL
    REFERENCES app.operadoras (operadora_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  ano           smallint NOT NULL CHECK (ano BETWEEN 2000 AND 2100),
  trimestre     smallint NOT NULL CHECK (trimestre BETWEEN 1 AND 4),

  -- Ajustado para numeric(18,2) conforme o SUM do seu script
  valor_despesas numeric(18,2) NOT NULL CHECK (valor_despesas >= 0),

  loaded_at     timestamptz NOT NULL DEFAULT now(),

  PRIMARY KEY (operadora_id, ano, trimestre)
);

-- =========================
-- GOLD: despesas_agregadas
-- =========================
DROP TABLE IF EXISTS app.despesas_agregadas;

CREATE TABLE app.despesas_agregadas (
  agg_id bigserial PRIMARY KEY,

  operadora_id bigint NULL
    REFERENCES app.operadoras (operadora_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,

  razao_social text NOT NULL,
  uf char(2) NULL,

  -- Campos ajustados para bater com a limpeza de regex do script
  total_despesas numeric(18,2) NULL,
  media_trimestral numeric(18,2) NULL,
  desvio_padrao_despesas numeric(18,2) NULL,

  loaded_at timestamptz NOT NULL DEFAULT now()
);

-- =========================
-- AUDIT: rejeitos_importacao
-- =========================
DROP TABLE IF EXISTS audit.rejeitos_importacao;

CREATE TABLE audit.rejeitos_importacao (
  rejeito_id      bigserial PRIMARY KEY,
  origem_arquivo  text NOT NULL,
  tabela_destino  text, -- Adicionado para suportar o segundo INSERT do script
  motivo          text NOT NULL,
  payload         jsonb NOT NULL,
  rejected_at     timestamptz NOT NULL DEFAULT now()
);