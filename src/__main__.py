# import required libraries
import discord # py-cord: discord bot framework
from discord.ext import commands
import logging # log handler
import asyncio # async functionality
import psycopg # postgres connector
import sys # stdout
import customio as io # db, env, ns 
import classes # auth, wa

# set up a logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(handler)

# read envvars
token, pgpass = io.env.load_envvars()

# set up the database
conn_uri = f"postgresql://ns-assembly:{pgpass}@ns-assembly-db:5432/ns-assembly"
postgres = io.db.Database(conn_uri)
postgres.setup_all()

# create the Bot object
bot = discord.Bot()

# define a method of fetching proposals
async def _fetch_proposals():
    for council in [1,2]:
        proposals = await io.ns.parse_proposals(council)        
        for proposal in proposals:
            await postgres.nsqueue_add(proposal)

async def _check_perms(ctx:discord.ApplicationContext, check_kind:str):
    authorised_role_id = await postgres.botperms_get_by_kind(check_kind)
    if authorised_role_id:
        authorised_role = await ctx.guild.fetch_role(authorised_role_id)
        if authorised_role in ctx.user.roles:
            return True
        else:
            return False
    else:
        return False

async def _get_queue_embed():
    await _fetch_proposals() # deprecated: in future versions this will no longer update on each command but instead on an event-driven basis
    queue = await postgres.nsqueue_get_all()
    table = ''
    for proposal in queue:
        if queue.index(proposal) <=2:
            status = 'Soon-to-vote'
        else:
            status = 'Quorum'
        table += f":green_circle: | {proposal.name} | {status} | N/A\n"
    embed = discord.Embed(
        title = 'WA Queue',
        description = table
    )
    return embed

# log when the bot starts up and has configured the database successfully
@bot.event
async def on_ready():
    logger.info('Bot ready')

# create info slash command
@bot.slash_command(name="info", description="Information about the bot")
async def info(ctx: discord.ApplicationContext):
    embed = discord.Embed(title = "Assembly v0.1.0-alpha-1", description = "For help or technical support message <@1271403487045095465> on Discord.")
    await ctx.respond(embed = embed, ephemeral = True)

@bot.slash_command(name="admin", description="Set admin role")
@commands.has_permissions(administrator = True) # must be an administrator to execute]
@discord.option("admin_role", description="Which role should be able to issue admin commands to the bot", type=discord.SlashCommandOptionType.role)
async def admin(ctx: discord.ApplicationContext, admin_role):
    await postgres.botperms_add(classes.auth.Permission().fromAttributeValues(kind = 'admin', identifier=admin_role.id))
    embed = discord.Embed(description="Admin role has been successfully set!")
    await ctx.respond(embed = embed, ephemeral = True)

@bot.slash_command(name="user", description="Set user role")
@commands.has_permissions(administrator = True)
@discord.option("user_role", description="Which role should be able to issue commands to the bot (note admins are automatically included)", type=discord.SlashCommandOptionType.role)
async def user(ctx: discord.ApplicationContext, user_role):
    await postgres.botperms_add(classes.auth.Permission().fromAttributeValues(kind = 'user', identifier=user_role.id))
    embed = discord.Embed(description="User role has been successfully set!")
    await ctx.respond(embed = embed, ephemeral = True)

# create slash command for fetching proposals
@bot.slash_command(name="fetch", description="Manually fetch proposals from the NS API")
async def fetch_proposals(ctx: discord.ApplicationContext):
    if await _check_perms(ctx, 'user'):
        await _fetch_proposals()
        embed = discord.Embed(title = 'Proposal Fetching', description = 'Latest proposals have been successfully fetched!')
    else:
        embed = discord.Embed(title = 'No Permissions', description = 'You do not have the required permissions to run this command.')
    await ctx.respond(embed = embed, ephemeral = True)

# create slash command for displaying fetched proposals
@bot.slash_command(name="queue", description="Display all proposals currently in the queue")
async def show_queue(ctx: discord.ApplicationContext):
    if await _check_perms(ctx, 'user'):
        embed = await _get_queue_embed()
        await ctx.respond(embed = embed, ephemeral = True)
    else:
        embed = discord.Embed(title = 'No Permissions', description = 'You do not have the required permissions to run this command.')
        await ctx.respond(embed = embed, ephemeral = True)

# and for advertising fetched proposals
@bot.slash_command(name="announce_queue", description="Announce all proposals currently in the queue to the current channel.")
@discord.option("ping_users", description="Whether or not to ping the specified user role.", type=discord.SlashCommandOptionType.boolean)
async def show_queue(ctx: discord.ApplicationContext,ping_users:bool):
    if await _check_perms(ctx, 'admin'):
        embed = await _get_queue_embed()
        if ping_users:
            ping = await postgres.botperms_get_by_kind('user')
            await ctx.respond(f'<@&{ping}>', embed = embed, ephemeral = False, allowed_mentions = discord.AllowedMentions(roles = True))
        else:
            await ctx.respond(embed = embed, ephemeral = False)
    else:
        embed = discord.Embed(title = 'No Permissions', description = 'You do not have the required permissions to run this command.')
        await ctx.respond(embed = embed, ephemeral = True)


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