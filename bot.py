import asyncio
from asyncore import loop
from dis import disco
from http.client import UnimplementedFileMode
import os
from turtle import title
from unicodedata import name
import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import time as t
import random as rand
import datetime

#All .env tokens, required for the bot to function without any modifications.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
NSFW_CHANNEL = int(os.getenv('DISCORD_NSFW_CHANNEL'))
ALERT_CHANNEL = int(os.getenv('DISCORD_ALERT_CHANNEL'))
COMMANDS_CHANNEL = int(os.getenv('DISCORD_COMMANDS_CHANNEL'))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)
bot.remove_command('help')


def reset_vars():
    global dead_members
    dead_members=[]

#Time since connection established loop
@tasks.loop(seconds=1)
async def time_connected_loop():
    global uptime
    #How the hell do presences work
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name='for +help; Online for 0 minutes.',state='Existing',details=f'Hello world!'))
    uptime=0
    #the update loop itself
    while True:
        await asyncio.sleep(1)
        uptime+=1
        if (uptime%60==0):
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f'for +help; Online for {uptime//60} minutes.',details=f'Hello world!'))


#Prints some data to terminal, also sends connected msg on COMMANDS_CHANNEL
@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in guild {guild.name}, ID: {guild.id}')
    members = f'\n - '.join([f'[{str(member.status).upper()}] {member.name}, ID = {member.id}' for member in guild.members])
    print(f'{len(guild.members)} Members on the server:\n - {members}')
    cmds_ch = bot.get_channel(COMMANDS_CHANNEL)

    activity = discord.Activity(type=discord.ActivityType.watching, name='for +help')
    await bot.change_presence(activity=activity)
    await cmds_ch.send(f'Connected to server!\nWatching for **+help**...')
    time_connected_loop.start()
    reset_vars()
    print("Started uptime loop!")


#detects if a message was sent in NSFW_CHANNEL, and sends a "spotted" alert in ALERTS_CHANNEL
@bot.event
async def on_message(message):
    if (message.author==bot.user):
        return

    if (message.channel.id==NSFW_CHANNEL):
        alerts = bot.get_channel(ALERT_CHANNEL)
        await alerts.send(f'{message.author} was spotted in the NSFW channel!!!')
        return
    
    await bot.process_commands(message)

#help command, pretty basic embed.
@bot.command()
async def help(ctx):
    embed_color=rand.randrange(1, 16777216)
    help_embed = discord.Embed(title="BWUBot help", description="Here you can find all currently available commands!",color=embed_color,timestamp=datetime.datetime.utcnow())
    help_embed.add_field(name="+help",value="Guess what this one does, I bet you can't.", inline=False)
    help_embed.add_field(name="+on?",value="Also works with: +status, +a?\nSends a response if the bot is on, along with the time it's been connected",inline=False)
    help_embed.add_field(name='+tips',value='Sends a random anxiety tip.',inline=False)
    help_embed.add_field(name="+kill [Message including a user(s) mention]",value="Kills the alive user(s) mentioned in the message",inline=False)
    help_embed.add_field(name="+revive [Message including a user(s) mention]",value="Revives the dead user(s) mentioned in the message",inline=False)
    help_embed.add_field(name="+dead",value="Sends a list of all dead members.",inline=False)

    
    await ctx.channel.send(embed=help_embed)


#V0C4LO1D's command idea
#Sends a random anxiety tip
@bot.command()
async def tips(ctx):
    tiplist=['When anxiety starts kicking in, count backwards repeatedly from 10 in your head.',
    'Close your eyes. Trust me, whenever you are trying to cope just close your eyes.',
    'Drink water. Focus on the feeling of it traveling down your throat, and into your chest.',
    'Fiddle with whatever resources you have around you',
    'Sing a song in your head. Distract yourself from what\'s going on around you. If it helps, cover your ears and distract from reality.']

    tip = 'Random anxiety tip by Charely:\n'

    tip+=rand.choice(tiplist)

    await ctx.channel.send(tip)

#Sends a message if the pot is online, along with the time since the connection was established.
@bot.command(name="on?", aliases = ['a?','status','uptime'])
async def isOn(ctx):
    uptimeS = uptime%60
    uptimeM = (uptime//60)%60
    uptimeH = uptime//3600
    await ctx.send(f"Hello world! I am currently online.\nTime since connected: {uptimeH}:{uptimeM}:{uptimeS}")

#Kill command, will go into more detail in the command
@bot.command()
async def kill(ctx):
    #Collects all mentions in message. If no mentions found returns a sort of error.
    mentions = ctx.message.mentions
    if not mentions:
        await ctx.send('Please mention member(s) to kill with an \'@\'')
        return
    for member in mentions:

        #Protects the creator (me) and other bots.
        if member.name == 'GM' and not f'{ctx.message.author.name}#{ctx.message.author.discriminator}' == 'GM#2372':
            await ctx.send('Please do not attempt to murder my creator.')
            return
        if member.bot:
            await ctx.send('Bots are immune to murder.')
            return
    
    #Sends a killed message with a few checks to check if there are multiple members, specifically who to kill and who is already dead, and if the member killed himself.
    killed ='Congrats. '
    #Multi person murder.
    if len(mentions)>=2:
        for member in mentions[0:-2]:
            if(not member in dead_members):
                killed += f'{member}, '
                dead_members.append(member)
            else:
                killed+=f'{member} was already dead, '

        if(not mentions[-2] in dead_members):
            killed += f'{mentions[-2]} '
            dead_members.append(mentions[-2])
        else:
            killed +=f'{mentions[-2]} was already dead '
        killed += 'and '
        if (not mentions[-1] in dead_members):
            killed += f'{mentions[-1]} were killed.'
            dead_members.append(mentions[-1])
        else:
            killed+= f'{mentions[-1]} was already dead. The rest were killed.'

    #One person murder.
    else:
        if(not mentions[0] in dead_members):
            dead_members.append(mentions[0])
            if(f'{ctx.message.author.name}#{ctx.message.author.discriminator}' == f'{mentions[0].name}#{mentions[0].discriminator}'):
                killed += f'{mentions[0]} has committed suicide.'
            else:
                killed += f'{mentions[0]} has been killed.'
        else:
            if(f'{ctx.message.author.name}#{ctx.message.author.discriminator}' == f'{mentions[0].name}#{mentions[0].discriminator}'):
                killed += f'{mentions[0]} has committed suicide. AGAIN.'
            else:
                killed += f'{mentions[0]} was already dead.'

    await ctx.send(killed)


@bot.command()
async def revive(ctx):

    #Kinda works like +kill, except the opposite for the checks with dead_members.
    mentions = ctx.message.mentions
    if not mentions:
        await ctx.send('Please mention member(s) to revive with an \'@\'')
        return
    for member in mentions:
        if member.name == 'GM' and not f'{ctx.message.author.name}#{ctx.message.author.discriminator}' == 'GM#2372':
            await ctx.send('As well as the intentions were, my creator is immune to murder and thus cannot be revived.')
            return
        if member.bot:
            await ctx.send('Bots are immune to murder.')
            return
    revived = "Thank you. "
    if len(mentions)>=2:
        for member in mentions[0:-2]:
            if(member in dead_members):
                revived += f'{member}, '
                dead_members.remove(member)
            else:
                revived+=f'{member} was not dead, '

        if(mentions[-2] in dead_members):
            revived += f'{mentions[-2]} '
            dead_members.remove(mentions[-2])
        else:
            revived +=f'{mentions[-2]} was not dead '
        revived += 'and '
        if (mentions[-1] in dead_members):
            revived += f'{mentions[-1]} were revived.'
            dead_members.remove(mentions[-1])
        else:
            revived+= f'{mentions[-1]} was not dead. The rest were revived.'
    
    else:
        if(mentions[0] in dead_members):
            dead_members.remove(mentions[0])
            if(f'{ctx.message.author.name}#{ctx.message.author.discriminator}' == f'{mentions[0].name}#{mentions[0].discriminator}'):
                revived += f'{mentions[0]} has revived himself, somehow.'
            else:
                revived += f'{mentions[0]} has been revived.'
        else:
            if(f'{ctx.message.author.name}#{ctx.message.author.discriminator}' == f'{mentions[0].name}#{mentions[0].discriminator}'):
                revived += f'{mentions[0]} has somehow revived himself even though he was already alive...?'
            else:
                revived += f'{mentions[0]} is not dead.'

    await ctx.channel.send(revived)
    
#Sends a list of all members in dead_members
@bot.command()
async def dead(ctx):
    dead = "Dead members (L):"
    for member in dead_members:
        dead+=f'\n - {member}'
    await ctx.send(dead)



@bot.command()
#this was wender_159's idea, not mine.
#please help me
async def uwu(ctx):
    await ctx.send('\"UwU\"')
    

bot.run(TOKEN)