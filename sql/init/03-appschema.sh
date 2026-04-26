#!/usr/bin/env bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c ns_assembly

    CREATE SCHEMA assembly;

    ALTER ROLE CURRENT_USER IN DATABASE ns_assembly SET search_path TO assembly;
    ALTER ROLE ns_assembly_app IN DATABASE ns_assembly SET search_path TO assembly;

    GRANT USAGE ON SCHEMA assembly TO ns_assembly_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA assembly TO ns_assembly_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA assembly GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ns_assembly_app;
EOSQL