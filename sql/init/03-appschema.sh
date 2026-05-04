#!/usr/bin/env bash

: 'This file is part of assembly.
Copyright (C) 2026 HippoProgrammer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \c ns_assembly

    CREATE SCHEMA assembly;

    ALTER ROLE CURRENT_USER IN DATABASE ns_assembly SET search_path TO assembly;
    ALTER ROLE ns_assembly_app IN DATABASE ns_assembly SET search_path TO assembly;

    GRANT USAGE ON SCHEMA assembly TO ns_assembly_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA assembly TO ns_assembly_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA assembly GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ns_assembly_app;
EOSQL