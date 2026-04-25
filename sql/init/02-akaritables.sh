#!/usr/bin/env bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c ns_akari
    CREATE SCHEMA akari;
    SET search_path = akari;
    GRANT ALL PRIVILEGES ON SCHEMA akari TO ns_akari;
    GRANT ALL PRIVILEGES ON SCHEMA akari TO ns_assembly_app;

    ALTER ROLE ns_assembly_app IN DATABASE ns_akari SET search_path = akari;
    ALTER ROLE ns_akari IN DATABASE ns_akari SET search_path = akari;

    SET ROLE ns_akari;
    ALTER DEFAULT PRIVILEGES IN SCHEMA akari GRANT SELECT, TRIGGER ON TABLES TO ns_assembly_app;
EOSQL