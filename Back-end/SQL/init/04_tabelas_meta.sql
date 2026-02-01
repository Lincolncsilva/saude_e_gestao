-- ============================================================
-- META — EVIDÊNCIA DE CARGAS
-- ============================================================


DROP TABLE IF EXISTS meta.cargas;

CREATE TABLE meta.cargas (
  carga_id          bigserial PRIMARY KEY,

  origem_arquivo    text NOT NULL,
  tabela_destino    text NULL,

  linhas_lidas      integer NOT NULL CHECK (linhas_lidas >= 0),
  linhas_rejeitadas integer NOT NULL CHECK (linhas_rejeitadas >= 0),

  loaded_at         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX cargas_origem_idx
  ON meta.cargas (origem_arquivo);

CREATE INDEX cargas_loaded_at_idx
  ON meta.cargas (loaded_at);