#!/bin/bash
set -euo pipefail

echo ">> [init] criando roles a partir de variáveis de ambiente"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
DO \$\$
BEGIN
  -- admin do banco (migrações/manutenção)
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'db_admin') THEN
    CREATE ROLE db_admin LOGIN PASSWORD '${POSTGRES_PASSWORD}' CREATEDB CREATEROLE;
  END IF;

  -- usuários/roles do projeto
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'etl_loader') THEN
    CREATE ROLE etl_loader LOGIN PASSWORD '${ETL_PASSWORD}';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'api_rw') THEN
    CREATE ROLE api_rw LOGIN PASSWORD '${API_PASSWORD}';
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'bi_ro') THEN
    CREATE ROLE bi_ro LOGIN PASSWORD '${BI_PASSWORD}';
  END IF;
END
\$\$;
EOSQL
