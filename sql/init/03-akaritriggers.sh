#!/usr/bin/env bash

: 'psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c ns_akari
    CREATE OR REPLACE FUNCTION create_new_sse_event_trigger() 
    RETURNS event_trigger 
    AS \$event\$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_event_trigger_ddl_commands() WHERE object_identity = 'public.akari_events%') THEN
                CREATE OR REPLACE FUNCTION notify_new_sse_event_on_insert() 
                RETURNS TRIGGER 
                AS \$trigger\$
                    BEGIN
                        NOTIFY new_sse_event, NEW.event;
                        RETURN NULL;
                    END;
                \$trigger\$ LANGUAGE plpgsql;

                CREATE TRIGGER new_sse_event_on_insert
                    AFTER INSERT ON akari_events
                    FOR EACH ROW EXECUTE FUNCTION notify_new_sse_event_on_insert();
            END IF;
        END;
    \$event\$ LANGUAGE plpgsql;

    CREATE EVENT TRIGGER create_sse_event_trigger_on_event
        ON ddl_command_end
        WHEN TAG IN ('CREATE TABLE')
        EXECUTE FUNCTION create_new_sse_event_trigger();
EOSQL'