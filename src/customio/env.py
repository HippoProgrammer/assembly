'''This file is part of assembly.
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
along with this program.  If not, see <https://www.gnu.org/licenses/>.'''

import os
import logging
from .exceptions import *

# set up a logger
logger = logging.getLogger('assembly.customio.env') # get the logger for this script

def load_secrets_from_envvars() -> tuple[str, str]:
    # load envvars 
    token_file = str(os.getenv("ASSEMBLY_TOKEN_FILE"))
    pgpass_file = str(os.getenv("POSTGRES_PASSWORD_FILE"))

    # sanity-check envvars
    if not os.path.isfile(token_file):
        raise exceptions.InvalidPathException('ASSEMBLY_TOKEN_FILE environment variable is not a valid path, cannot start')
    if not os.path.isfile(pgpass_file):
        raise exceptions.InvalidPathException('POSTGRES_PASS_FILE environment variable is not a valid path, cannot start')

    # read token file
    with open(token_file,'r') as file:
        token = file.read()

    # read passfile
    with open(pgpass_file,'r') as file:
        pgpass = file.read()
    return token, pgpass

def load_database_config_from_envvars() -> tuple[str, str, str, str, str]:
    user = str(os.getenv("POSTGRES_USER"))
    host = str(os.getenv("POSTGRES_HOST"))
    port = str(os.getenv("POSTGRES_PORT"))
    assembly_db = str(os.getenv("POSTGRES_ASSEMBLY_DB"))
    akari_db = str(os.getenv("POSTGRES_AKARI_DB"))
    return user, host, port, assembly_db, akari_db

def load_useragent_from_envvars() -> str:
    useragent_nation = str(os.getenv("NS_USER_AGENT"))
    return useragent_nation