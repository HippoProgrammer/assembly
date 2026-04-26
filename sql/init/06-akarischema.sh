#!/usr/bin/env bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c ns_akari
    
    CREATE SCHEMA akari;

    ALTER ROLE CURRENT_USER IN DATABASE ns_akari SET search_path TO akari;
    ALTER ROLE ns_assembly_app IN DATABASE ns_akari SET search_path TO akari;
    ALTER ROLE ns_akari IN DATABASE ns_akari SET search_path TO akari;

    GRANT ALL PRIVILEGES ON SCHEMA akari TO ns_akari;
    GRANT ALL PRIVILEGES ON SCHEMA akari TO ns_assembly_app;
    ALTER DEFAULT PRIVILEGES FOR ROLE ns_akari IN SCHEMA akari GRANT ALL ON TABLES TO ns_akari;
    ALTER DEFAULT PRIVILEGES FOR ROLE ns_akari IN SCHEMA akari GRANT SELECT, TRIGGER ON TABLES TO ns_assembly_app;
EOSQL