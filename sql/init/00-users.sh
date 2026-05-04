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

app_pass="$(<$APP_PASSWORD_FILE)"
akari_pass="$(<$AKARI_PASSWORD_FILE)"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER ns_assembly_app ENCRYPTED PASSWORD '${app_pass}';
    CREATE USER ns_akari ENCRYPTED PASSWORD '${akari_pass}';
EOSQL
