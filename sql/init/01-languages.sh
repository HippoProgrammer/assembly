#!/usr/bin/env bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT USAGE ON LANGUAGE plpgsql TO ns_assembly_app;
    GRANT USAGE ON LANGUAGE plpgsql TO ns_akari;
EOSQL

