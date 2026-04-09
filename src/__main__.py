# import required libraries
import discord # py-cord: discord bot framework
import logging # log handler
import asyncio # async functionality
import psycopg # postgres connector
import os, sys # general os-level functionality

# set up a logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# load envvars 
token_file = str(os.getenv("ASSEMBLY_TOKEN_FILE"))
pgpass_file = str(os.getenv("POSTGRES_PASSWORD_FILE"))
logger.info('Envvars loaded')

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
logger.info('Token read')

# read passfile
with open(pgpass_file,'r') as file:
    pgpass = file.read()
logger.info('Password read')

conn_uri = f"postgresql://ns-assembly:{pgpass}@ns-assembly-db:5432/ns-assembly"

# database setup
# check if the requisite tables already exist
with psycopg.connect(conn_uri) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS NSQueue (
            ID VARCHAR(63) PRIMARY KEY,
            Council TINYINT CHECK (Council = 1 OR Council = 2),
            Name VARCHAR(63) NOT NULL,
            Category VARCHAR(63) NOT NULL,
            Author VARCHAR(31) NOT NULL,
            Coauthor_1 VARCHAR(31),
            Coauthor_2 VARCHAR(31),
            Coauthor_3 VARCHAR(31),
            Legal BOOL
            );
            """) # create a table for storing queued proposal information, direct from the NS API
        cur.execute("""
            CREATE TABLE IF NOT EXISTS IFVQueue (
            ID VARCHAR(63) PRIMARY KEY,
            Thread INT NOT NULL,
            IFVAuthor INT,
            IFVLink VARCHAR(63)
            );
            """) # create a table for storing IFV information, such as assigned authors and regional positions
        conn.commit() # save changes to DB

# create the Bot object
bot = discord.Bot()

# log when the bot starts up
@bot.event
async def on_ready():
    logger.info('Bot ready')

# create slash command for creating and advertising IFVs
@bot.slash_command(name="advertise", description="Advertise IFVs to server members",guild_ids=[1491504463851159603])
async def advertise_ifv(ctx: discord.ApplicationContext):
    async def add_ifv_callback(interaction):
        # SET UP CALLBACKS HERE
        pass
    async def remove_ifv_callback(interaction):
        # SET UP CALLBACKS HERE
        pass
    add_ifv = discord.ui.Button(label='Add IFV')
    remove_ifv = discord.ui.Button(label='Remove IFV')
    add_ifv.callback = add_ifv_callback
    remove_ifv.callback = remove_ifv_callback

    # generate a View with Buttons added
    view = discord.ui.View()
    view.add_item(add_ifv)
    view.add_item(remove_ifv)

    await ctx.respond(view=view, ephemeral=True)

bot.run(token)