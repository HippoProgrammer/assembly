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

    CREATE TABLE IF NOT EXISTS NSQueue (
    ID TEXT PRIMARY KEY,
    Council SMALLINT CHECK (Council = 1 OR Council = 2),
    Name TEXT NOT NULL,
    Category TEXT NOT NULL,
    Author TEXT NOT NULL,
    Coauthors TEXT ARRAY[3],
    Legal BOOL NOT NULL,
    Quorum BOOL NOT NULL
    ); -- create a table for storing queued proposal information, direct from the NS API

    CREATE TABLE IF NOT EXISTS IFVQueue (
    ID TEXT PRIMARY KEY,
    Name TEXT NOT NULL,
    Thread BIGINT NOT NULL,
    IFVAuthor BIGINT,
    IFVLink TEXT
    ); -- create a table for storing IFV information, such as assigned authors and regional positions. 

    CREATE TABLE IF NOT EXISTS BotPerms (
    Kind TEXT PRIMARY KEY,
    Identifier BIGINT NOT NULL
    ); -- create a table for storing perms

    CREATE TABLE IF NOT EXISTS ChannelReference (
    Kind TEXT PRIMARY KEY,
    Identifier BIGINT NOT NULL
    ); -- create a table for storing channels
EOSQL