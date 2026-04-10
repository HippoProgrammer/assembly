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
handler = logging.StreamHandler(stream=sys.stdout)
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
            await postgres.ifvqueue_add(classes.ifv.IFV().fromAttributeValues(proposal.id)) # deprecated: in future releases this will be moved to the thread creation function

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
    table = 'Stance | Name | Status | IFV Author | IFV Link\n'
    for proposal in queue:
        ifv = await postgres.ifvqueue_get_by_id(proposal.id)
        name = proposal.name
        if queue.index(proposal) <=2:
            status = 'Soon-to-vote'
        else:
            status = 'Quorum'
        if ifv.ifvauthor == None:
            author = 'N/A'
        else:
            author = f'<@{ifv.ifvauthor}>'
        if ifv.ifvlink == None:
            link = 'N/A'
        else:
            link = f'[{ifv.ifvlink}](Link)'
        table += f":green_circle: | {name} | {status} | {author} | {link} \n"
    embed = discord.Embed(
        title = 'WA Queue',
        description = table
    )
    return embed

class IFVSubmissionModal(discord.ui.Modal):
    def __init__(self, id:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_id = id
        self.add_item(discord.ui.InputText(label="Link to your IFV:", placeholder='https://www.nationstates.net/page=dispatch/id=2612787'))
    async def update_by_submission_modal(self, interaction):
        await postgres.ifvqueue_update_link_by_id(id = self.custom_id, link = self.children[0].value)

class IFVView(discord.ui.View):
    async def _get_select_options_from_ifvs(self, ifvs:list):
        return [discord.SelectOption(label=(await postgres.nsqueue_get_by_id(ifv.id)).name, value=ifv.id) for ifv in ifvs]
    @discord.ui.button(style = discord.ButtonStyle.primary,custom_id = 'accept',label = 'Accept IFV')
    async def button_accept_ifv_callback(self, button, interaction):
        await interaction.response.defer()
        self.get_item('submit').disabled = True
        self.get_item('remove').disabled = True
        self.get_item('select').disabled = False
        ifvs = await postgres.ifvqueue_get_unauthored()
        self.get_item('select').options = await self._get_select_options_from_ifvs(ifvs[:25])
        self.custom_action = 'accept'
        await interaction.edit_original_response(view=self) # update the message
    @discord.ui.button(style = discord.ButtonStyle.success,custom_id = 'submit',label = 'Submit IFV')
    async def button_submit_ifv_callback(self, button, interaction):
        self.get_item('accept').disabled = True
        self.get_item('remove').disabled = True
        self.get_item('select').disabled = False
        ifvs = await postgres.ifvqueue_get_by_author(interaction.user.id)
        self.get_item('select').options = await self._get_select_options_from_ifvs(ifvs[:25])
        self.custom_action = 'submit'
        await interaction.edit_original_response(view=self)
    @discord.ui.button(style = discord.ButtonStyle.danger,custom_id = 'remove',label = 'Remove IFV')
    async def button_remove_ifv_callback(self, button, interaction):
        await interaction.response.defer()
        self.get_item('submit').disabled = True
        self.get_item('accept').disabled = True
        self.get_item('select').disabled = False
        ifvs = await postgres.ifvqueue_get_by_author(interaction.user.id)
        self.get_item('select').options = await self._get_select_options_from_ifvs(ifvs[:25])
        self.custom_action = 'remove' 
        await interaction.edit_original_response(view=self)
    @discord.ui.select(placeholder = 'Select an IFV',min_values = 1,max_values = 1,options = [discord.SelectOption(label="No IFVs loaded.")],custom_id = 'select',disabled = True)
    async def select_ifv_callback(self, select, interaction):
        await interaction.response.defer()
        if self.custom_action == 'accept':
            await postgres.ifvqueue_update_author_by_id(id = select.values[0], author = interaction.user.id)
        elif self.custom_action == 'submit':
            # send a modal
            await interaction.response.send_modal(IFVSubmissionModal(title="IFV Submission", id = select.values[0]))
        elif self.custom_action == 'remove':
            await postgres.ifvqueue_remove(id = select.values[0])
        self.get_item('accept').disabled = False
        self.get_item('submit').disabled = False
        self.get_item('remove').disabled = False
        self.get_item('select').disabled = True
        embed = await _get_queue_embed()
        await interaction.edit_original_response(view=self,embed=embed)
    async def on_error(self, error: Exception, item, interaction: discord.Interaction):
        # This catches errors from any component in the View
        raise error


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