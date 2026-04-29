import os
import logging

# set up a logger
logger = logging.getLogger('assembly.customio.env') # get the logger for this script

def load_secrets_from_envvars():
    # load envvars 
    token_file = str(os.getenv("ASSEMBLY_TOKEN_FILE"))
    pgpass_file = str(os.getenv("POSTGRES_PASSWORD_FILE"))

    # sanity-check envvars
    if not os.path.isfile(token_file):
        msg = 'ASSEMBLY_TOKEN_FILE environment variable is not a valid path, cannot start'
        logger.error(msg)
        raise Exception(msg)
    if not os.path.isfile(pgpass_file):
        msg = 'POSTGRES_PASS_FILE environment variable is not a valid path, cannot start'
        logger.error(msg)
        raise Exception(msg)

    # read token file
    with open(token_file,'r') as file:
        token = file.read()

    # read passfile
    with open(pgpass_file,'r') as file:
        pgpass = file.read()
    return token, pgpass

def load_useragent_from_envvars():
    useragent_nation = str(os.getenv("NS_USER_AGENT"))
    return useragent_nation