#!/bin/python
# import required libraries
import discord # py-cord: discord bot framework
from discord.ext import commands
import logging # log handler
import asyncio # async functionality
import psycopg # postgres connector
import sys # stdout
import customio as io # db, env, ns 
import classes # auth, wa
import traceback

# set up a logger
logger = logging.getLogger(__name__) # get the logger for this script
handler = logging.StreamHandler(stream=sys.stdout) # set logs to be sent to stdout
logger.addHandler(handler) # attach the handler to the logger
logger.setLevel(logging.DEBUG) # set the logs to output at debug verbosity

# read envvars
token, pgpass = io.env.load_envvars() # load environment variables (bot token, postgres db password)

# set up the database
conn_uri = f"postgresql://ns-assembly:{pgpass}@ns-assembly-db:5432/ns-assembly" # create a standard postgres connection URI by inserting the loaded password
postgres = io.db.Database(conn_uri) # create a DB instance

# create the Bot object
bot = discord.Bot() # create a bot instance

# define a method of fetching proposals
async def _fetch_proposals() -> None:
    """Fetch World Assembly proposals from the NS API, for both councils, into the database."""
    for council in [1,2]: # for each council
        proposals = await io.ns.parse_proposals(council) # load a parsed version of the proposals from the API        
        for proposal in proposals: # for each proposal
            await postgres.nsqueue_add(proposal) # add it to the NSQueue table
            await postgres.ifvqueue_add(classes.ifv.IFV().fromAttributeValues(proposal.id,proposal.name)) # deprecated: in future releases this will be moved to the thread creation function

async def _check_perms(ctx:discord.ApplicationContext, check_kind:str) -> bool:
    """Check if the permissions of a supplied user match those stored in the database."""
    authorised_role_id = await postgres.botperms_get_by_kind(check_kind) # fetch the id of the actual authorised role from the DB
    if authorised_role_id: # if it exists
        authorised_role = await ctx.guild.fetch_role(authorised_role_id) # fetch the Role object from the Discord API using the id
        if authorised_role in ctx.user.roles: # if the user has the Role
            return True # they are authorised
        else: # otherwise
            return False # they are not authorised
    else: # if the id does not exist, it must not have been set
        return False # so nobody is authorised

async def _get_queue_embed() -> discord.Embed:
    """Get an embed with the World Assembly proposal queue included."""
    await _fetch_proposals() # deprecated: in future versions this will no longer update on each command but instead on an event-driven basis
    queue = await postgres.nsqueue_get_all() # fetch all proposals in the NSQueue table
    table = 'Stance | Name | Status | IFV Author | IFV Link\n' # create a table, starting with the header
    for proposal in queue: # for each fetched proposal
        ifv = await postgres.ifvqueue_get_by_id(proposal.id) # get its corresponding IFV entry
        name = proposal.name # redefine the name
        if queue.index(proposal) <=2: # if the proposal is within the top 3
            status = 'Soon-to-vote' # it is soon-to-vote
        else: # otherwise
            status = 'Quorum' # it is merely at quorum
        if ifv.ifvauthor == None: # if no IFV author is listed
            author = 'N/A' # represent this in a human-readable format
        else: # if one is listed
            author = f'<@{ifv.ifvauthor}>' # tag their Discord user id
        if ifv.ifvlink == None: # if no IFV link is listed
            link = 'N/A' # represent this in a human-readable format
        else: # if one is listed
            link = f'[Link]({ifv.ifvlink})' # link this in Markdown syntax
        table += f":green_circle: | {name} | {status} | {author} | {link} \n" # add all this data to the table
    embed = discord.Embed(
        title = 'WA Queue',
        description = table
    ) # put the table in an embed
    return embed # return it

class IFVSelectionModal(discord.ui.DesignerModal):
    def __init__(self, user_id:int, action:str, options_data:list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.action = action
        self.user_id = user_id

        options = [discord.SelectOption(label=option.name,value=option.id) for option in options_data]

        self.add_item(discord.ui.Label(
            label = 'IFV:',
            description = f'Select which IFV you would like to {action}.',
            item = discord.ui.StringSelect(
                placeholder = 'Select an IFV...',
                min_values = 1,
                max_values = 1,
                options = options,
                custom_id = 'select'
            )
        ))

        if action == 'submit':
            self.add_item(discord.ui.Label(
                label = 'Link to IFV:',
                description = 'A link to your IFV. This should NOT be a NationStates dispatch until approval has been gained.',
                item = discord.ui.InputText(
                    placeholder = 'https://docs.google.com/document/abcdefghijklmnopqrstuvwxyz0123456789abcdefij',
                    custom_id = 'link'
                )
                
            ))

    async def callback(self, interaction):
        success = discord.Embed(description = "IFV modified successfully!").set_footer(text = 'The queue embed may take 1-5 seconds to refresh.')
        failure_invalid_link = discord.Embed(description = "IFV was not modified.").set_footer(text = 'Please provide a link that is not a NationStates dispatch.')
        if self.action == 'accept':
            await postgres.ifvqueue_update_author_by_id(id = self.get_item('select').values[0], author = self.user_id)
            await interaction.respond(embed = success, ephemeral = True)
        elif self.action == 'submit':
            if 'nationstates.net' not in self.get_item('link').value :
                await postgres.ifvqueue_update_link_by_id(id = self.get_item('select').values[0], link = self.get_item('link').value)
                await interaction.respond(embed = success, ephemeral = True)
            else:
                await interaction.respond(embed = failure_invalid_link, ephemeral = True)
        elif self.action == 'remove':
            await postgres.ifvqueue_remove(id = self.get_item('select').values[0])
            await interaction.respond(embed = success, ephemeral = True)

class IFVView(discord.ui.View):
    async def _button(self, button, interaction):
        action = button.custom_id
        user_id = interaction.user.id
        if button.custom_id == 'accept':
            options_data = await postgres.ifvqueue_get_unauthored_limited()
        else:
            options_data = await postgres.ifvqueue_get_by_author(user_id)
        modal = IFVSelectionModal(user_id = user_id, action = action, options_data = options_data, title='IFV Modification')
        await interaction.response.send_modal(modal)
        await modal.wait()
        await interaction.edit_original_response(view=self, embed = await _get_queue_embed())

    @discord.ui.button(label="Accept IFV", style=discord.ButtonStyle.success, custom_id='accept')
    async def accept(self, button, interaction):
        await self._button(button, interaction)

    @discord.ui.button(label="Submit IFV", style=discord.ButtonStyle.primary, custom_id='submit')
    async def submit(self, button, interaction):
        await self._button(button, interaction)

    @discord.ui.button(label="Remove IFV", style=discord.ButtonStyle.danger, custom_id='remove')
    async def remove(self, button, interaction):
        await self._button(button, interaction)

    async def on_error(self, error, item, interaction):
        print(f"Error in {item}: {error}")
        traceback.print_exception(type(error), error, error.__traceback__)

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
        await ctx.respond(embed = embed, ephemeral = True, view=IFVView())
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
            await ctx.respond(f'<@&{ping}>', embed = embed, ephemeral = False, allowed_mentions = discord.AllowedMentions(roles = True), view=IFVView())
        else:
            await ctx.respond(embed = embed, ephemeral = False, view=IFVView())
    else:
        embed = discord.Embed(title = 'No Permissions', description = 'You do not have the required permissions to run this command.')
        await ctx.respond(embed = embed, ephemeral = True)

async def main():
    try:
        await postgres.setup_all() # run standard setup scripts
        await bot.start(token)
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        await postgres.cleanup()
        
asyncio.run(main())