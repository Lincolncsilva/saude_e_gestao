-- ============================================================
-- RAW (Bronze / Staging)
-- Tabelas de staging para receber os CSVs sem tipagem rígida
-- ============================================================

CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS raw.stg_operadoras_ans;
CREATE TABLE raw.stg_operadoras_ans (
  registro_operadora          text,
  cnpj                        text,
  razao_social                text,
  nome_fantasia               text,
  modalidade                  text,
  logradouro                  text,
  numero                      text,
  complemento                 text,
  bairro                      text,
  cidade                      text,
  uf                          text,
  cep                         text,
  ddd                         text,
  telefone                    text,
  fax                         text,
  endereco_eletronico         text,
  representante               text,
  cargo_representante         text,
  regiao_de_comercializacao   text,
  data_registro_ans           text
);

DROP TABLE IF EXISTS raw.stg_consolidado_despesas;
CREATE TABLE raw.stg_consolidado_despesas (
  cnpj          text,
  razaosocial   text,
  trimestre     text,
  ano           text,
  valordespesas text,
  cnpj_valido   text,
  valor_valido  text,
  rs_valida     text
);

DROP TABLE IF EXISTS raw.stg_despesas_agregadas;
CREATE TABLE raw.stg_despesas_agregadas (
  razaosocial             text,
  uf                     text,
  total_despesas         text,
  media_trimestral       text,
  desvio_padrao_despesas text
);
