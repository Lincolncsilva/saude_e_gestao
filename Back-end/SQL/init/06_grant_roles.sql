
-- 1) Revogando permissao de criar objetos no schema public
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- 2) Garantir ownership dos schemas (requer superuser/owner)
ALTER SCHEMA raw   OWNER TO db_admin;
ALTER SCHEMA app   OWNER TO db_admin;
ALTER SCHEMA bi    OWNER TO db_admin;
ALTER SCHEMA audit OWNER TO db_admin;
ALTER SCHEMA meta  OWNER TO db_admin;

-- 3) USAGE nos schemas
GRANT USAGE ON SCHEMA raw, app, bi, audit, meta TO db_admin;
GRANT USAGE ON SCHEMA raw, app, audit TO etl_loader;
GRANT USAGE ON SCHEMA app, bi TO api_rw;
GRANT USAGE ON SCHEMA bi TO bi_ro;

-- 4) Permissões em objetos existentes
-- db_admin: controle total
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw, app, bi, audit, meta TO db_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA raw, app, bi, audit, meta TO db_admin;

-- etl_loader: staging + carga no silver + escrita em audit
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA raw TO etl_loader;
GRANT SELECT, INSERT, UPDATE         ON ALL TABLES IN SCHEMA app TO etl_loader;
GRANT INSERT                         ON ALL TABLES IN SCHEMA audit TO etl_loader;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA app, audit, meta TO etl_loader;

-- api_rw: CRUD no silver + leitura no gold
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO api_rw;
GRANT SELECT                         ON ALL TABLES IN SCHEMA bi TO api_rw;
GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA app TO api_rw;

-- bi_ro: leitura analítica
GRANT SELECT ON ALL TABLES IN SCHEMA bi TO bi_ro;

-- 5) Default privileges para objetos FUTUROS
-- Aplica para o usuário que executa este script
ALTER DEFAULT PRIVILEGES IN SCHEMA raw
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO etl_loader;

ALTER DEFAULT PRIVILEGES IN SCHEMA app
  GRANT SELECT, INSERT, UPDATE ON TABLES TO etl_loader;

ALTER DEFAULT PRIVILEGES IN SCHEMA audit
  GRANT INSERT ON TABLES TO etl_loader;

ALTER DEFAULT PRIVILEGES IN SCHEMA app
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO api_rw;

ALTER DEFAULT PRIVILEGES IN SCHEMA bi
  GRANT SELECT ON TABLES TO api_rw;

ALTER DEFAULT PRIVILEGES IN SCHEMA bi
  GRANT SELECT ON TABLES TO bi_ro;

-- Default privileges para sequences futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA app
  GRANT USAGE, SELECT ON SEQUENCES TO api_rw;

ALTER DEFAULT PRIVILEGES IN SCHEMA app
  GRANT USAGE, SELECT ON SEQUENCES TO etl_loader;

ALTER DEFAULT PRIVILEGES IN SCHEMA audit
  GRANT USAGE, SELECT ON SEQUENCES TO etl_loader;

ALTER DEFAULT PRIVILEGES IN SCHEMA meta
  GRANT USAGE, SELECT ON SEQUENCES TO etl_loader;

-- 6) search_path por role (conveniência)
ALTER ROLE etl_loader SET search_path = raw, app, audit, meta;
ALTER ROLE api_rw     SET search_path = app, bi;
ALTER ROLE bi_ro      SET search_path = bi;
ALTER ROLE db_admin   SET search_path = raw, app, bi, audit, meta, public;
