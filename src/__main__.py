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
import datetime

# set up a logger
logger = logging.getLogger(__name__) # get the logger for this script
handler = logging.StreamHandler(stream=sys.stdout) # set logs to be sent to stdout
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler) # attach the handler to the logger
logger.setLevel(logging.DEBUG) # set the logs to output at debug verbosity
logger.info('Logging started')

# read envvars
token, pgpass = io.env.load_envvars() # load environment variables (bot token, postgres db password)
logger.info('Environment variables loaded')

# set up the database
conn_uri = f"postgresql://ns-assembly:{pgpass}@ns-assembly-db:5432/ns-assembly" # create a standard postgres connection URI by inserting the loaded password
logger.debug('Connection URI created')
postgres = io.db.Database(conn_uri) # create a DB instance
logger.debug('Database object created')

# create the Bot object
bot = discord.Bot() # create a bot instance
logger.debug('Bot object created')

# define a method of creating threads
async def _create_thread_ifv_for_proposal(proposal:classes.wa.Proposal) -> None:
    """Given a Proposal object, create a thread with its information in a designated channel and add that information to the IFVQueue table."""
    channel = bot.get_channel(await postgres.channelref_get_by_kind('thread')) # get channel from ID stored in DB
    logger.debug('Thread channel object found')

    name = proposal.name # reassign name
    id = proposal.id # reassign id
    author = proposal.author.replace('_',' ').title() # replace underscores with spaces and capitalize author name
    if proposal.coauthors: # if there are coauthors
        coauthors = ', '.join(proposal.coauthors).replace('_',' ').title() # do the same formatting for them
    else: # otherwise
        coauthors = 'N/A' # mark as N/A
    link = f'[Link to proposal text](https://nationstates.net/page=UN_view_proposal/id={id})' # format the link in Markdown syntax
    logger.debug('Proposal information formatted')

    embed = discord.Embed(
        title=name,
        description=f"Author: {author} | Coauthor(s): {coauthors}\n{link}" # add coauthor support later
    ) # create an embed using this information
    logger.debug('Embed object created')

    thread = await channel.create_thread(name=name, embed=embed, reason='Created WA proposal thread. Automatic action by Assembly bot.') # Create a thread using the embed earlier
    logger.info('Thread created')

    message = thread.starting_message # get the message just sent
    logger.debug('Message object found')

    await message.add_reaction('🟢') # add required reactions
    await message.add_reaction('🔴')
    logger.info('Reactions added')

    await postgres.ifvqueue_add(classes.ifv.IFV().fromAttributeValues(id=id,name=name,thread=thread.id)) # add information and thread ID to IFVQueue
    logger.info('Proposal added to IFVQueue')

# define a method of fetching proposals
async def _fetch_proposals() -> None:
    """Fetch World Assembly proposals from the NS API, for both councils, into the database."""
    for council in [1,2]: # for each council
        logger.debug('New council')

        proposals = await io.ns.parse_proposals(council) # load a parsed version of the proposals from the API   
        logger.info('Proposal data fetched from API')

        for proposal in proposals: # for each proposal
            if proposal.legal and proposal.quorum:
                logger.debug('Proposal legal and at quorum')

                await postgres.nsqueue_add(proposal) # add it to the NSQueue table
                logger.info('Proposal added to NSQueue')

                await _create_thread_ifv_for_proposal(proposal) # create a thread and add it to the IFVQueue table
                logger.info('Proposal thread being created')
        logger.info('Proposal data parsed and stored')

# define a method to check user perms for slash commands
async def _check_perms(ctx:discord.ApplicationContext, check_kind:str) -> bool:
    """Check if the permissions of a supplied user match those stored in the database."""

    authorised_role_id = await postgres.botperms_get_by_kind(check_kind) # fetch the id of the actual authorised role from the DB
    logger.debug('Authorised role ID fetched from DB')

    if authorised_role_id: # if it exists
        authorised_role = await ctx.guild.fetch_role(authorised_role_id) # fetch the Role object from the Discord API using the id
        logger.debug('Authorised role object found')

        if authorised_role in ctx.user.roles: # if the user has the Role
            logger.info('User has authorised role, approving')
            return True # they are authorised
        else: # otherwise
            logger.info('User does not have authorised role, rejecting')
            return False # they are not authorised
    else: # if the id does not exist, it must not have been set
        logger.info('Authorised role ID not set, rejecting')
        return False # so nobody is authorised

# define a method to get the embed for the WA queue
async def _get_queue_embed() -> discord.Embed:
    """Get an embed with the World Assembly proposal queue included."""
    await _fetch_proposals() # deprecated: in future versions this will no longer update on each command but instead on an event-driven basis

    queue = await postgres.nsqueue_get_all() # fetch all proposals in the NSQueue table
    logger.debug('Proposals fetched from DB')

    table = 'Stance | Name | Status | IFV Author | IFV Link\n' # create a table, starting with the header
    logger.debug('Table header created')

    for proposal in queue: # for each fetched proposal
        logger.debug('New proposal')

        ifv = await postgres.ifvqueue_get_by_id(proposal.id) # get its corresponding IFV entry
        logger.debug('Proposal IFV entry fetched from DB')

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
        
        reactions = bot.get_channel(ifv.thread).starting_message.reactions
        green = [react for react in reactions if react.emoji == '🟢'][0].count
        red = [react for react in reactions if react.emoji == '🔴'][0].count

        if green == red:
            emoji = '🟢/🔴'
        elif green > red:
            emoji = '🟢'
        else:
            emoji = '🔴'
        
        logger.debug('Proposal information formatted')

        table += f"{emoji} | {name} | {status} | {author} | {link} \n" # add all this data to the table
        logger.debug('Proposal information added to table')
    embed = discord.Embed(
        title = 'WA Queue',
        description = table,
        timestamp = datetime.datetime.now()
    ) # put the table in an embed
    logger.info('Embed object created')
    return embed # return it

# define class for IFV modals
class IFVSelectionModal(discord.ui.DesignerModal):
    def __init__(self, user_id:int, action:str, options_data:list, *args, **kwargs) -> None:
        """Create an IFVSelectionModal object, for selecting and modifying IFV details."""
        super().__init__(*args, **kwargs) # pass args and kwargs to base class
        logger.debug('Args and kwargs passed to base Modal')

        self.action = action # 'save' important variables in object properties
        self.user_id = user_id

        options = [discord.SelectOption(label=option.name,value=option.id) for option in options_data] # format raw DB data into SelectOptions
        
        self.valid = bool(len(options)) # if any options are present, the Modal can be classed as valid
        logger.debug('Options and properties parsed and formatted')

        if not self.valid: # if there are no options, add a placeholder to keep the API happy
            options = [discord.SelectOption(label='No modifiable IFVs.')]
            logger.debug('Options invalid, placeholder option created')

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
        )) # add the options to a Labelled StringSelect and add that to the Modal
        logger.debug('Select created')

        if action == 'submit' and self.valid: # if this modal is valid and we need a submission
            self.add_item(discord.ui.Label(
                label = 'Link to IFV:',
                description = 'A link to your IFV. This should NOT be a NationStates dispatch until approval has been gained.',
                item = discord.ui.InputText(
                    placeholder = 'https://docs.google.com/document/abcdefghijklmnopqrstuvwxyz0123456789abcdefij',
                    custom_id = 'link'
                )
            )) # add a box for the link
            logger.debug('Link created')
        
        logger.debug('Modal initialized')

    async def callback(self, interaction):
        """Callback for an IFVSelectionModal."""

        success = discord.Embed(description = "IFV modified successfully!").set_footer(text = 'The queue embed may take 1-5 seconds to refresh.')
        failure_invalid_link = discord.Embed(description = "IFV was not modified.").set_footer(text = 'Please provide a link that is not a NationStates dispatch.')
        failure_invalid_options = discord.Embed(description = "IFV was not selected.").set_footer(text = 'You have no valid IFVs for the selected action!')
        logger.debug('Embed objects formatted and created')

        if not self.valid: # if invalid
            await interaction.respond(embed = failure_invalid_options, ephemeral = True) # send an embed informing the user that they selected an invalid option
            logger.debug('Modal invalid, sent error message')
        elif self.action == 'accept': # if valid and accept is the action
            await postgres.ifvqueue_update_author_by_id(id = self.get_item('select').values[0], author = self.user_id) # mark the IFV as accepted in the DB
            logger.debug('IFVQueue updated with author')

            await interaction.respond(embed = success, ephemeral = True) # send a success message
            logger.debug('Sent success message')
        elif self.action == 'submit': # if valid and submit is the action
            if 'nationstates.net' not in self.get_item('link').value: # and the link does not contain invalid websites
                await postgres.ifvqueue_update_link_by_id(id = self.get_item('select').values[0], link = self.get_item('link').value) # save the link to the IFV on the DB
                logger.debug('IFVQueue updated with link')

                await interaction.respond(embed = success, ephemeral = True) # send a success message
                logger.debug('Sent success message')
            else: # if link is invalid
                await interaction.respond(embed = failure_invalid_link, ephemeral = True) # send an embed informing the user that their link was invalid
                logger.debug('Link invalid, sent error message')
        elif self.action == 'remove': # if valid and remove is the action
            await postgres.ifvqueue_remove(id = self.get_item('select').values[0]) # remove the accepted mark and the link from the DB
            logger.debug('IFVQueue updated with removed data')

            await interaction.respond(embed = success, ephemeral = True) # send a success message
            logger.debug('Sent success message')

# define class for IFV view
class IFVView(discord.ui.View):
    async def _button(self, button, interaction):
        """Private method to handle button callbacks."""
        action = button.custom_id # redefine some basic information
        user_id = interaction.user.id
        logger.debug('Interaction data formatted and stored')

        if button.custom_id == 'accept': # if the IFV is to be accepted
            options_data = await postgres.ifvqueue_get_unauthored_limited() # fetch acceptable IFVs
        else: # otherwise
            options_data = await postgres.ifvqueue_get_by_author(user_id) # fetch the author's IFVs
        logger.debug('Option data fetched from DB')

        modal = IFVSelectionModal(user_id = user_id, action = action, options_data = options_data, title='IFV Modification') # put all info into a modal
        logger.debug('Modal object created')

        await interaction.response.send_modal(modal) # send the modal
        logger.info('Modal sent - waiting for submission')
        await modal.wait() # wait until it has been submitted
        await interaction.edit_original_response(view=self, embed = await _get_queue_embed()) # then refresh the embed with the new info
        logger.info('Modal submitted, embed refreshed')

    @discord.ui.button(label="Accept IFV", style=discord.ButtonStyle.success, custom_id='accept') # accept IFV button
    async def accept(self, button, interaction): # pass onto _button handler
        await self._button(button, interaction)

    @discord.ui.button(label="Submit IFV", style=discord.ButtonStyle.primary, custom_id='submit') # submit IFV button
    async def submit(self, button, interaction): # pass onto _button handler
        await self._button(button, interaction)

    @discord.ui.button(label="Remove IFV", style=discord.ButtonStyle.danger, custom_id='remove') # remove IFV button
    async def remove(self, button, interaction): # pass onto _button handler
        await self._button(button, interaction)
    
    @discord.ui.button(label="Refresh Queue", style=discord.ButtonStyle.secondary, custom_id='refresh') # refresh embed button
    async def refresh(self, button, interaction):
        await interaction.edit_original_response(view=self, embed = await _get_queue_embed()) # refresh embed
        logger.info('Embed refreshed at user command')

    async def on_error(self, error, item, interaction): # deprecated
        print(f"Error in {item}: {error}")
        traceback.print_exception(type(error), error, error.__traceback__)

# log when the bot starts up and has configured the database successfully
@bot.event
async def on_ready() -> None:
    logger.info('Bot started, ready for interaction')

# create info slash command
@bot.slash_command(name="info", description="Information about the bot")
async def info(ctx: discord.ApplicationContext) -> None:
    embed = discord.Embed(title = "Assembly v0.1.0-alpha-1", description = "For help or technical support message <@1271403487045095465> on Discord.")
    logger.debug('Embed object created')

    await ctx.respond(embed = embed, ephemeral = True)
    logger.info('Info embed sent')

@bot.slash_command(name="admin", description="Set admin role")
@commands.has_permissions(administrator = True) # must be an administrator to execute]
@discord.option("admin_role", description="Which role should be able to issue admin commands to the bot", type=discord.SlashCommandOptionType.role)
async def admin(ctx: discord.ApplicationContext, admin_role) -> None:
    await postgres.botperms_add(classes.auth.Permission().fromAttributeValues(kind = 'admin', identifier=admin_role.id))
    logger.info('Admin role set')

    embed = discord.Embed(description="Admin role has been successfully set!")
    logger.debug('Embed object created')

    await ctx.respond(embed = embed, ephemeral = True)
    logger.info('Success embed sent')

@bot.slash_command(name="user", description="Set user role")
@commands.has_permissions(administrator = True)
@discord.option("user_role", description="Which role should be able to issue commands to the bot (note admins are automatically included)", type=discord.SlashCommandOptionType.role)
async def user(ctx: discord.ApplicationContext, user_role) -> None:
    await postgres.botperms_add(classes.auth.Permission().fromAttributeValues(kind = 'user', identifier=user_role.id))
    logger.info('User role set')
    
    embed = discord.Embed(description="User role has been successfully set!")
    logger.debug('Embed object created')

    await ctx.respond(embed = embed, ephemeral = True)
    logger.info('Success embed sent')

@bot.slash_command(name="thread", description="Set proposal thread channel")
@commands.has_permissions(administrator = True)
@discord.option("thread_channel", description="Which channel should have proposal threads automatically created in it", type=discord.SlashCommandOptionType.channel)
async def thread(ctx: discord.ApplicationContext, thread_channel) -> None:
    await postgres.channelref_add(classes.auth.Channel().fromAttributeValues(kind = 'thread', identifier=thread_channel.id))
    logger.info('Thread channel set')
    
    embed = discord.Embed(description="Thread channel has been successfully set!")
    logger.debug('Embed object created')
    
    await ctx.respond(embed = embed, ephemeral = True)
    logger.info('Success embed sent')

# create slash command for fetching proposals
@bot.slash_command(name="fetch", description="Manually fetch proposals from the NS API")
async def fetch_proposals(ctx: discord.ApplicationContext) -> None:
    if await _check_perms(ctx, 'user'):
        logger.info('Fetching proposals')
        await _fetch_proposals()
        logger.info('Proposals fetched')

        embed = discord.Embed(title = 'Proposal Fetching', description = 'Latest proposals have been successfully fetched!')
        logger.debug('Embed object created')
    else:
        embed = discord.Embed(title = 'No Permissions', description = 'You do not have the required permissions to run this command.')
        logger.debug('Embed object created')
    await ctx.respond(embed = embed, ephemeral = True)
    logger.info('Response embed sent')

# create slash command for displaying fetched proposals
@bot.slash_command(name="queue", description="Display all proposals currently in the queue")
async def show_queue(ctx: discord.ApplicationContext) -> None:
    if await _check_perms(ctx, 'user'):
        logger.info('Fetching queue embed')
        embed = await _get_queue_embed()
        logger.info('Queue embed fetched')

        await ctx.respond(embed = embed, ephemeral = True, view=IFVView())
        logger.info('Queue embed sent')
    else:
        embed = discord.Embed(title = 'No Permissions', description = 'You do not have the required permissions to run this command.')
        logger.debug('Embed object created')

        await ctx.respond(embed = embed, ephemeral = True)
        logger.info('Error embed sent')

# and for advertising fetched proposals
@bot.slash_command(name="announce_queue", description="Announce all proposals currently in the queue to the current channel.")
@discord.option("ping_users", description="Whether or not to ping the specified user role.", type=discord.SlashCommandOptionType.boolean)
async def show_queue(ctx: discord.ApplicationContext,ping_users:bool) -> None:
    if await _check_perms(ctx, 'admin'):
        logger.info('Fetching queue embed')
        embed = await _get_queue_embed()
        logger.info('Queue embed fetched')

        if ping_users:
            ping = await postgres.botperms_get_by_kind('user')
            logger.debug('Ping role id found')

            await ctx.respond(f'<@&{ping}>', embed = embed, ephemeral = False, allowed_mentions = discord.AllowedMentions(roles = True), view=IFVView())
            logger.info('Queue embed sent (announced) and pinged')
        else:
            await ctx.respond(embed = embed, ephemeral = False, view=IFVView())
            logger.info('Queue embed sent (announced)')
    else:
        embed = discord.Embed(title = 'No Permissions', description = 'You do not have the required permissions to run this command.')
        logger.debug('Embed object created')

        await ctx.respond(embed = embed, ephemeral = True)
        logger.info('Error embed sent')

async def main() -> None:
    try:
        logger.info('Starting DB setup scripts')
        await postgres.setup_all() # run standard setup scripts
        logger.info('DB setup scripts completed')

        logger.info('Starting bot')
        await bot.start(token)
        logger.info('Bot started')
    except asyncio.exceptions.CancelledError:
        logger.warning('asyncio.exceptions.CancelledError was suppressed - was a SIGINT sent?')
        pass
    finally:
        logger.critical('Program terminating - was a SIGINT sent?')

        logger.info('Starting DB cleanup scripts')
        await postgres.cleanup()
        logger.info('DB cleanup scripts completed')

        logger.critical('Program terminated')
        
asyncio.run(main())