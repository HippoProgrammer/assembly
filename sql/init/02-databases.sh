#!/usr/bin/env bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE ns_assembly;
    GRANT CONNECT ON DATABASE ns_assembly TO ns_assembly_app;

    CREATE DATABASE ns_akari;
    GRANT CONNECT ON DATABASE ns_akari TO ns_assembly_app;
    GRANT ALL ON DATABASE ns_akari TO ns_akari;
EOSQL