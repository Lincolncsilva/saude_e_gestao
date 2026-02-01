-- ============================================================
-- CAMADA SILVER (APP)
-- Tabelas tipadas, normalizadas e prontas para API / Analytics
-- ============================================================

-- =========================
-- DIMENSÃO: OPERADORAS
-- =========================

DROP TABLE IF EXISTS app.operadoras CASCADE;

CREATE TABLE app.operadoras (
  operadora_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

  -- chaves de negócio
  registro_operadora varchar(20) NOT NULL UNIQUE,
  cnpj              varchar(14) NOT NULL UNIQUE,

  -- dados cadastrais
  razao_social      text NOT NULL,
  nome_fantasia     text,
  modalidade        text,

  -- endereço
  logradouro        text,
  numero            text,
  complemento       text,
  bairro            text,
  cidade            text,
  uf                char(2),
  cep               varchar(8),

  -- contato
  ddd               varchar(3),
  telefone          varchar(30),
  fax               varchar(30),
  endereco_eletronico text,

  -- representante
  representante     text,
  cargo_representante text,

  -- metadados ANS
  regiao_de_comercializacao smallint,
  data_registro_ans date,

  -- controle
  created_at timestamptz NOT NULL DEFAULT now(),

  -- validações leves
  CONSTRAINT operadoras_uf_chk
    CHECK (uf IS NULL OR uf ~ '^[A-Z]{2}$'),

  CONSTRAINT operadoras_cnpj_chk
    CHECK (cnpj ~ '^[0-9]{14}$')
);

-- Índices para API e análises
CREATE INDEX operadoras_uf_idx
  ON app.operadoras (uf);

CREATE INDEX operadoras_razao_idx
  ON app.operadoras USING btree (razao_social);

CREATE INDEX operadoras_modalidade_idx
  ON app.operadoras (modalidade);

-- =========================
-- FATO: DESPESAS CONSOLIDADAS
-- Granularidade: operadora x ano x trimestre
-- =========================

DROP TABLE IF EXISTS app.despesas_consolidadas;

CREATE TABLE app.despesas_consolidadas (
  operadora_id  bigint NOT NULL
    REFERENCES app.operadoras (operadora_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  ano           smallint NOT NULL
    CHECK (ano BETWEEN 2000 AND 2100),

  trimestre     smallint NOT NULL
    CHECK (trimestre BETWEEN 1 AND 4),

  valor_despesas numeric(18,2) NOT NULL
    CHECK (valor_despesas >= 0),

  loaded_at     timestamptz NOT NULL DEFAULT now(),

  PRIMARY KEY (operadora_id, ano, trimestre)
);

-- ============================================================
-- AUDIT — REGISTRO DE REJEITOS DE IMPORTAÇÃO
-- ============================================================

DROP TABLE IF EXISTS audit.rejeitos_importacao;

CREATE TABLE audit.rejeitos_importacao (
  rejeito_id     bigserial PRIMARY KEY,

  -- origem
  origem_arquivo text NOT NULL,
  tabela_destino text NOT NULL,

  -- motivo técnico/negócio
  motivo         text NOT NULL,

  -- linha original (payload bruto)
  payload        jsonb NOT NULL,

  -- metadados
  rejected_at   timestamptz NOT NULL DEFAULT now()
);

-- Índices para auditoria e troubleshooting
CREATE INDEX rejeitos_importacao_origem_idx
  ON audit.rejeitos_importacao (origem_arquivo);

CREATE INDEX rejeitos_importacao_data_idx
  ON audit.rejeitos_importacao (rejected_at);

-- Índices analíticos
CREATE INDEX despesas_cons_periodo_idx
  ON app.despesas_consolidadas (ano, trimestre);

CREATE INDEX despesas_cons_operadora_idx
  ON app.despesas_consolidadas (operadora_id);

-- =========================
-- FATO AUXILIAR: DESPESAS AGREGADAS
-- Granularidade: Razão Social x UF
-- operadora_id é opcional (mapeado heurístico por razão social)
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

  total_despesas numeric(18,2) NULL
    CHECK (total_despesas IS NULL OR total_despesas >= 0),

  media_trimestral numeric(18,2) NULL
    CHECK (media_trimestral IS NULL OR media_trimestral >= 0),

  desvio_padrao_despesas numeric(18,2) NULL
    CHECK (desvio_padrao_despesas IS NULL OR desvio_padrao_despesas >= 0),

  loaded_at timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT despesas_agg_uf_chk
    CHECK (uf IS NULL OR uf ~ '^[A-Z]{2}$')
);

-- Índices para consumo por UF / API
CREATE INDEX despesas_agg_uf_idx
  ON app.despesas_agregadas (uf);

CREATE INDEX despesas_agg_operadora_idx
  ON app.despesas_agregadas (operadora_id);

CREATE INDEX despesas_agg_razao_idx
  ON app.despesas_agregadas USING btree (razao_social);
