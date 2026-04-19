#!/usr/bin/env bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c ns_akari
    CREATE OR REPLACE FUNCTION create_new_sse_event_trigger() RETURNS event_trigger AS $create_event_trigger$
        BEGIN
            CREATE OR REPLACE FUNCTION notify_new_sse_event_on_insert() RETURNS TRIGGER as $notify_new_sse_event$
                BEGIN
                    NOTIFY new_sse_event;
                    RETURN NULL;
                END;
            $notify_new_sse_event$ LANGUAGE plpgsql;

            CREATE TRIGGER new_sse_event_on_insert
                AFTER INSERT ON akari_events
                FOR EACH STATEMENT EXECUTE FUNCTION notify_new_sse_event_on_insert();
        END;
    $create_event_trigger$ LANGUAGE plpgsql;

    CREATE EVENT TRIGGER create_sse_event_trigger_on_event
        ON ddl_command_end
        WHEN TAG IN ('CREATE TABLE')
        EXECUTE FUNCTION create_new_sse_event_trigger()
EOSQL