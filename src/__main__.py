# import required libraries
import discord # py-cord: discord bot framework
import logging # log handler
import asyncio # async functionality
import psycopg # postgres connector
import sys # stdout
import db # database
import ns # nationstates API
import env # env vars
import wa # wa classes

# set up a logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# read envvars
token, pgpass = env.load_envvars()

# set up the database
conn_uri = f"postgresql://ns-assembly:{pgpass}@ns-assembly-db:5432/ns-assembly"
postgres = db.Database(conn_uri)
postgres.setup()

# create the Bot object
bot = discord.Bot()

# define a method of fetching proposals
async def _fetch_proposals():
    for council in [1,2]:
        proposals = await ns.parse_proposals(council)        
        for proposal in proposals:
            postgres.add_proposal(proposal)

# log when the bot starts up
@bot.event
async def on_ready():
    logger.info('Bot ready')

# create slash command for fetching proposals
@bot.slash_command(name="fetch", description="Fetch listed proposals",guild_ids=[1491504463851159603])
async def fetch_proposals(ctx: discord.ApplicationContext):
    await _fetch_proposals()
    await ctx.respond("Latest proposals have been successfully fetched!")    

# create slash command for displaying fetched proposals
@bot.slash_command(name="queue", description="Display all proposals currently in the queue",guild_ids=[1491504463851159603])
async def send_queue(ctx: discord.ApplicationContext):
    await _fetch_proposals()
    queue = postgres.get_queue()
    table = ''
    for proposal in queue:
        table += f":green_circle: | {proposal.name} | Quorum | N/A\n"
    embed = discord.Embed(
        description = table
    )
    await ctx.respond(embed = embed)
"""
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
"""
bot.run(token)