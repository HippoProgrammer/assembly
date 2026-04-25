#!/usr/bin/env bash

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