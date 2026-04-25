#!/usr/bin/env bash

app_pass="$(<$APP_PASSWORD_FILE)"
akari_pass="$(<$AKARI_PASSWORD_FILE)"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER ns_assembly_app ENCRYPTED PASSWORD '${app_pass}';
    CREATE USER ns_akari ENCRYPTED PASSWORD '${akari_pass}';
EOSQL
