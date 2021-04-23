from configparser import Error
from discord.ext.commands import *
from discord.ext import commands
from discord import activity
import discord
import datetime
import asyncio
import json
import random
import os

#? Get Bot Data initialization class.
if os.path.exists("BotData.py"):
    import BotData
else:
    raise Exception("BotData.py Does not exist!")


THIS_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)  #? Get relative path to our folder.
CONFIG_FILE_PATH = os.path.join(
    THIS_FOLDER, "botconfig.cfg"
)  #? Create path of config file. (name can be changed)
DATETIME_OBJ = datetime.datetime
STARTUP_TIME = DATETIME_OBJ.now()

#? Our bot data object.
BOT_DATA = BotData.BotData()
#? Json database file path.
USER_CHANNELS_JSON_PATH = THIS_FOLDER + "/user_channels.json"
#? Initialize the json database.
BOT_DATA.read_json(USER_CHANNELS_JSON_PATH)

#? Read essential files.
try:
    BOT_DATA.read_config_data(CONFIG_FILE_PATH)
except Exception as e:
    print(f"{e}")
    exit()


#? Create and Initialize Bot object.
BOT = Bot(
    command_prefix=BOT_DATA.BOT_PREFIX,
    description="Bot by Raz Kissos, helper and useful functions.",
)  #? Create the discord bot.
BOT.remove_command("help")  #? Remove default `help` command (will replace later).


@BOT.event
async def on_ready():
    """
    This function sends a message in the console telling us the bot is up.
    it also configures the bot's status and sends the data to the servers.
    """
    BOT_DATA.BOT_NAME = BOT.user.name
    activity_info = activity.Activity(
        type=activity.ActivityType.listening, name="{}help".format(BOT_DATA.BOT_PREFIX)
    )
    await BOT.change_presence(activity=activity_info, status=BOT_DATA.STATUS)


def print_guilds():
    print("********************")
    print("Current servers: ")
    for server in BOT.guilds:
        print("- " + server.name)
    print("********************")


async def list_servers():
    """
    This function prints the bot's connected server list every hour.
    """
    await BOT.wait_until_ready()
    while not BOT.is_closed():
        print_guilds()
        print(
            "{}\nBot by Raz Kissos, helper and useful functions.\n********************\n".format(
                DATETIME_OBJ.today()
            )
        )
        await asyncio.sleep(3600) # Wait one hour.
    print("Bot is closing...")
    await asyncio.sleep(1)


async def send_success_embed(ctx: Context, title: str="Success", text: str="", footer: str = ""):
    embed = discord.Embed(color=discord.Color.green(), title=f"✅ {title} ✅", description=text)
    embed.set_footer(text=footer)
    await ctx.send(embed=embed)

async def send_warning_embed(ctx: Context, title: str="Warning", text: str="", footer: str = ""):
    embed = discord.Embed(color=discord.Color.dark_gold(), title= f"⚠️ {title} ⚠️", description=text)
    embed.set_footer(text=footer)
    await ctx.send(embed=embed)

async def send_error_embed(ctx: Context, title: str="Error", text: str="", footer: str = ""):
    embed = discord.Embed(color=discord.Color.red(), title=f"🛑 {title} 🛑", description=text)
    embed.set_footer(text=footer)
    await ctx.send(embed=embed)


@BOT.event
async def on_command_error(ctx, error: Error):
    """
    Excepts every error the bot receivs and prints it to the console.
    @param ctx (discord.ext.commands.Context): the command context object.
    @param error (from discord.errors): the excepted error.
    """
    print("[!] ERROR: {}\n{}".format(error.args, error))


#? Create Asynchronous tasks for the bot before running:
asyncio.ensure_future(
    list_servers()
)  #? Run the `list_servers` function as an asynchronous coroutine.


@BOT.command(
    name="help",
    aliases=["h"],
    brief="Shows the help message.\nAlso can be used as a single command help message.",
    description="When sent with no arguments, the command simply prints out all the command names and their brief explanations. But when sending a command name as an argument the command will print out a full list of the command's fields.",
    usage=f"| **{BOT_DATA.BOT_PREFIX}help** -> print out the full list of commands.\n| **{BOT_DATA.BOT_PREFIX}help <command name>** - > print out thorough description of the command with the matching name",
)
async def help(ctx, command_name: str = None):
    """
    This command replaces the default help command from discord and sends a prettier and formatted help message.
    @param ctx (discord.ext.commands.Context): the command context object.
    @param command_name (str): the command name to get data about (optional).
    """

    if command_name is None:  # Check if help was invoked as a specific command help.
        # Create return embed
        author = ctx.message.author
        embed = discord.Embed(color=discord.Color.gold())
        embed.set_thumbnail(url=BOT.user.avatar_url)
        embed.set_footer(text="Senior Bot's Commands")

        for cmd in BOT.commands:
            embed.add_field(
                name=str(f"♿|**{BOT_DATA.BOT_PREFIX}{cmd.name}**: "),
                value=str(f"❓ {cmd.brief}"),
                inline=False,
            )
        await ctx.send(
            embed=embed
        )  # Send the shallow info of each command as an embed.
    else:  # Help command was invoked as a specific command help.
        # Check if command name is actually a command.
        if command_name in [command.name for command in BOT.commands]:
            # Get the requested command object.
            cmd_to_print = None
            for cmd in BOT.commands:
                if cmd.name == command_name:
                    cmd_to_print = cmd
                    break

            # Check if command has any aliases, if not return 'None'.
            if len(cmd_to_print.aliases) == 0:
                aliases_str = "None"
            else:
                aliases_str = ", ".join(
                    [f'"{alias}"' for alias in cmd_to_print.aliases]
                )

            # Create and send the thorough command info embed.
            embed = discord.Embed(color=discord.Color.dark_orange())
            embed.set_footer(text=f'"{cmd_to_print.name}" thorough description')
            embed.add_field(
                name="💬 Command Name 💬", value=cmd_to_print.name, inline=False
            )
            embed.add_field(
                name="❓ Brief Explanation ❓", value=cmd_to_print.brief, inline=False
            )
            embed.add_field(
                name="📰 Description 📰", value=cmd_to_print.description, inline=False
            )
            embed.add_field(
                name="⚙ Command Usage ⚙", value=cmd_to_print.usage, inline=False
            )
            embed.add_field(
                name="🎭 Command Name Aliases 🎭", value=aliases_str, inline=False
            )
            await ctx.channel.send(embed=embed)
        else:  # Command name was not found in the bot's commands.
            await ctx.channel.send(f"No command named {command} was found!")


@BOT.command(
    name="botinfo",
    aliases=["bot"],
    brief="Shows general information about the bot.",
    description="Shows the bot information (startup time, github page, etc...).",
    usage=f"| **{BOT_DATA.BOT_PREFIX}botinfo** -> will print an embed with the general bot information.",
)
async def botinfo(ctx):
    """
    This command sends an embed to the context's channel which will contain general bot information.
    @param ctx (discord.ext.commands.Context): the command context object.
    """
    print(STARTUP_TIME)
    embed_ret = discord.Embed(colour=discord.Color.green(), timestamp=ctx.message.created_at, title=f"Bot Info")
    embed_ret.set_thumbnail(url=BOT.user.avatar_url)
    embed_ret.add_field(name="❓ Name ❔", value=BOT.user.name)
    embed_ret.add_field(name="❓ Nickame ❔", value=BOT.user.display_name)
    embed_ret.add_field(name="⏰ Running Since ⏰", value=STARTUP_TIME.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
    
    def strfdelta(tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)
    
    embed_ret.add_field(name="🕗 Total Runtime 🕑", value=strfdelta((DATETIME_OBJ.now() - STARTUP_TIME), "{days} days {hours}:{minutes}:{seconds}"), inline=False)
    embed_ret.add_field(name="🌍 All Guilds 🌎", value='\n'.join([str('- ' + guild.name) for guild in BOT.guilds]), inline=False)
    embed_ret.set_footer(text="Bot Information")
    await ctx.channel.send(embed=embed_ret)  # Send the embed.


@BOT.command(
    name="create_pvc",
    aliases=['create', 'pvc'],
    brief="Create a private voice channel for you and your friends.",
    description="Creates a private voice channel.",
    usage=f"| **{BOT_DATA.BOT_PREFIX}create_pvc @member1 @member2 ...** -> will create a private voice channel on the `private voice channels` category on the server."
    )
async def create_pvc(ctx, *member_tags):
    guild: discord.Guild = ctx.guild
    categories: list = guild.categories
    pvc_category: discord.CategoryChannel = None
    for category in categories:
        if category.name == '🔒private voice channels🔒':
            pvc_category = category
    
    if pvc_category is None:
        pvc_category = await guild.create_category('🔒private voice channels🔒')

    author_member_obj: discord.Member = await guild.fetch_member(int(ctx.message.author.id))

    with open(USER_CHANNELS_JSON_PATH, 'r') as f:
        json_obj: dict = json.loads(f.read())
    
    author_data: tuple = json_obj.get(str(author_member_obj.id), None)
    if author_data is not None:
        #? Author already has an existing group.
        existing_role: discord.Role = guild.get_role(int(author_data[0]))
        existing_group: discord.VoiceChannel = guild.get_channel(int(author_data[1]))
        if existing_role is not None and existing_group is not None:
            await send_warning_embed(ctx, 'Group Already Exists', f'You already have an existing group named {existing_role.mention} with a correspoding private vc named {existing_group.name}!')
            return
        else:
            await send_error_embed(ctx, "Database Error", f'Deleting your existing group due to database error (you have probably deleted your role manually)!\nPlease make sure to delete all instances of the group (role and vc) or contact your administrator!\nCreating new group...')

            #? Update the json database.
            with open(USER_CHANNELS_JSON_PATH, 'w') as f:
                del json_obj[str(author_member_obj.id)]
                f.write(json.dumps(json_obj))

    
    #> If we reach this point then the author does not have an existing group.

    #? Fetch tagged members and add them to the group.
    tagged_members = list()
    for member_tag in member_tags:
        member_id: str = member_tag[3:-1]
        member_obj: discord.Member = await guild.fetch_member(int(member_id))
        if member_obj is None:
            await send_warning_embed(ctx, "Member not Found", f'Could not find member with the corresponding id `{member_id}`!')
            continue
        tagged_members.append(member_obj)
    
    #? Add author just in case and convert to set to get rid of duplicates.
    tagged_members.append(author_member_obj)
    tagged_members = list(set(tagged_members))

    #? Create new private role and assign to group members.
    new_role: discord.Role = await guild.create_role(name=f"{ctx.author.name}'s Private Group", mentionable=True, colour=discord.Color.random())
    for member in tagged_members:
        await member.add_roles(new_role)

    #? Create vc permissions to only allow the role's members to connect.
    everyone_perms = {'connect': False, 'speak': False}
    role_perms = {'connect': True, 'speak': True}
    overwrites = {
        guild.default_role : discord.PermissionOverwrite(**everyone_perms),
        new_role: discord.PermissionOverwrite(**role_perms)
    }
    vc:discord.VoiceChannel = await pvc_category.create_voice_channel(f"{ctx.author.name}'s Private Voice Channel", user_limit=len(tagged_members), overwrites=overwrites)

    #? Save new info to json database.
    json_obj[str(author_member_obj.id)] = (str(new_role.id), str(vc.id))
    with open(USER_CHANNELS_JSON_PATH, 'w') as f:
        f.write(json.dumps(json_obj))
    
    await send_success_embed(ctx, "Group Created Successfully", f'Successfully created a private voice channel {vc.name} for members {", ".join([member.mention for member in tagged_members])}!')

@BOT.command(
    name="purge_pvc",
    aliases=['purge', 'yeet'],
    brief="Delete a private voice channel that belongs to you.",
    description="Deletes a user's private voice channel.",
    usage=f"| **{BOT_DATA.BOT_PREFIX}purge_pvc** -> will delete the author's private voice channel from the server and delete the role related to it."
    )
async def purge_pvc(ctx):
    guild: discord.Guild = ctx.guild
    author_member_obj: discord.Member = await guild.fetch_member(int(ctx.message.author.id))
    with open(USER_CHANNELS_JSON_PATH, 'r') as f:
        json_obj: dict = json.loads(f.read())
    
    author_data: tuple = json_obj.get(str(author_member_obj.id), None)
    if author_data is None:
        #? Author has no existing group.
        await send_warning_embed(ctx, "No Existing Group", f'You have no existing private group in the database!')
        return
    
    existing_role: discord.Role = guild.get_role(int(author_data[0]))
    existing_vc: discord.VoiceChannel = guild.get_channel(int(author_data[1]))

    if existing_role and existing_vc:
        #? Delete the user's private group's role and vc.
        await existing_role.delete()
        await existing_vc.delete()
    else:
        await send_error_embed(ctx, "Currupted Database", f'An error occured in the database, deleting information from the database! Please contanct your admin or remove the problematic group by hand!')
    
    #> If we have reached this point then we know the author has an existing group.
    
    #? Update the json database.
    with open(USER_CHANNELS_JSON_PATH, 'w') as f:
        del json_obj[str(author_member_obj.id)]
        f.write(json.dumps(json_obj))

    await send_success_embed(ctx, "Group Deleted Successfully", "The private group was successfully deleted!")


@BOT.command(
    name="add_members",
    aliases=['add'],
    brief="Add members to your private voice channel.",
    description="Adds members to a private voice channel.",
    usage=f"| **{BOT_DATA.BOT_PREFIX}add_members @member1 @member2 ...** -> will add the list of tagged members to the owner's private voice channel."
    )
async def add_members(ctx, *member_tags):
    guild: discord.Guild = ctx.guild

    with open(USER_CHANNELS_JSON_PATH, 'r') as f:
        json_obj: dict = json.loads(f.read())
    
    author_data: tuple = json_obj.get(str(ctx.author.id), None)
    if author_data is not None:
        #? Author already has an existing group.
        existing_role: discord.Role = guild.get_role(int(author_data[0]))
        existing_group: discord.VoiceChannel = guild.get_channel(int(author_data[1]))
        if existing_role is not None and existing_group is not None:
            #? Fetch tagged members and add them to the group.
            tagged_members = list()
            for member_tag in set(member_tags):
                member_id: str = member_tag[3:-1]
                try:
                    member_obj: discord.Member = await guild.fetch_member(int(member_id))
                except Exception as e:
                    #! We tried to fetch a bot or a non existant user.
                    await send_warning_embed(ctx, "Member not Found", f'Could not find member with the corresponding id `{member_id}`!')
                    continue
                if existing_role not in member_obj.roles:
                    await member_obj.add_roles(existing_role)
                    tagged_members.append(member_obj)
                else:
                    await send_warning_embed(ctx, "Member Already in Group", f'{member_obj.mention} is already in the private group {existing_role.mention}!')
                    continue
            
            await existing_group.edit(user_limit = existing_group.user_limit + len(tagged_members))
            await send_success_embed(ctx, "Members Added Successfully", f'Successfully added members {", ".join([member.mention for member in tagged_members])} to the private voice channel {existing_group.name}!')
            return
        else:
            await send_error_embed(ctx, "Database Error", f'Please make sure to delete all instances of the group (role and vc) or contact your administrator!\nPlease create a new private group!', "You have probably deleted your role manually")

            #? Update the json database.
            with open(USER_CHANNELS_JSON_PATH, 'w') as f:
                del json_obj[str(ctx.author.id)]
                f.write(json.dumps(json_obj))
            
            return
    else:
            send_warning_embed(ctx, "No Existing Group", f'You have no existing private group! please create one!')
            return


@BOT.command(
    name="remove_members",
    aliases=['remove', 'kick'],
    brief="Remove members from your private voice channel.",
    description="Removes members from a private voice channel.",
    usage=f"| **{BOT_DATA.BOT_PREFIX}remove_members @member1 @member2 ...** -> will remove the list of tagged members from the owner's private voice channel."
    )
async def remove_members(ctx, *member_tags):
    guild: discord.Guild = ctx.guild

    with open(USER_CHANNELS_JSON_PATH, 'r') as f:
        json_obj: dict = json.loads(f.read())
    
    author_data: tuple = json_obj.get(str(ctx.author.id), None)
    if author_data is not None:
        #? Author already has an existing group.
        existing_role: discord.Role = guild.get_role(int(author_data[0]))
        existing_group: discord.VoiceChannel = guild.get_channel(int(author_data[1]))
        if existing_role is not None and existing_group is not None:
            #? Fetch tagged members and add them to the group.
            tagged_members = list()
            for member_tag in set(member_tags):
                member_id: str = member_tag[3:-1]
                try:
                    member_obj: discord.Member = await guild.fetch_member(int(member_id))
                except Exception as e:
                    #! We tried to fetch a bot or a non existant user.
                    await send_warning_embed(ctx, "Member not Found", f'Could not find member with the corresponding id `{member_id}`!')
                    continue
                if existing_role in member_obj.roles:
                    await member_obj.remove_roles(existing_role)
                    tagged_members.append(member_obj)
                else:
                    await send_warning_embed(ctx, "Member Not in Group", f'{member_obj.mention} is not in the private group {existing_role.mention}!')
                    continue
            
            if len(tagged_members) == 0:
                await send_error_embed(ctx, "Not Successful", f'Could not remove any members from the private voice channel {existing_group.name}!')
            elif (existing_group.user_limit - len(tagged_members)) > 0:
                await existing_group.edit(user_limit = existing_group.user_limit - len(tagged_members))
                await send_success_embed(ctx, "Members Removed Successfully", f'Successfully removed members {", ".join([member.mention for member in tagged_members])} from the private voice channel {existing_group.name}!')
            else:
                await send_error_embed(ctx, "Error", "Please contact your administrator or try again later.")
            return
        else:
            await send_warning_embed(ctx, "No Existing Group", f'You have no existing private group! please create one!')
            return

#> Finally, Run the Bot!
BOT.run(BOT_DATA.TOKEN)