#!/usr/bin/env bash

app_pass="$(<$APP_PASSWORD_FILE)"
akari_pass="$(<$AKARI_PASSWORD_FILE)"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c ns_akari
    GRANT ALL PRIVILEGES ON SCHEMA public TO ns_akari;
EOSQL