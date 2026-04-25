#!/usr/bin/env bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c ns_assembly
    
    CREATE INDEX IF NOT EXISTS NSQueue_ID_index ON NSQueue (ID); -- create relevant indexes on frequently-queried tables
    CREATE INDEX IF NOT EXISTS IFVQueue_Author_index on IFVQueue (IFVAuthor);
EOSQL