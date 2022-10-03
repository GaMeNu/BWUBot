from asyncore import loop
import os
from unicodedata import name
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time as t
import random as rand


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
NSFW_CHANNEL = int(os.getenv('DISCORD_NSFW_CHANNEL'))
ALERT_CHANNEL = int(os.getenv('DISCORD_ALERT_CHANNEL'))
COMMANDS_CHANNEL = int(os.getenv('DISCORD_COMMANDS_CHANNEL'))

intents = discord.Intents.default()
intents.members=True
intents.message_content=True
bot = commands.Bot(command_prefix='+', intents=intents)

@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in guild {guild.name}, ID: {guild.id}')
    members = f'\n - '.join([f'[{member.status}] {member.name}, ID = {member.id}' for member in guild.members])
    print(f'{len(guild.members)} Members on the server:\n - {members}')
    cmds_ch = bot.get_channel(COMMANDS_CHANNEL)
    await cmds_ch.send(f'Connected to server!')

@bot.event
async def on_message(message):
    if (message.author==bot.user):
        return

    if (message.channel.id==NSFW_CHANNEL):
        alerts = bot.get_channel(ALERT_CHANNEL)
        await alerts.send(f'{message.author} was spotted in the NSFW channel!!!')
        return
    
    await bot.process_commands(message)

@bot.command()
async def test(ctx):
    print('command recieved!')
    await ctx.send("Hello world!")

@bot.command()
async def kill(ctx, *args):
    
    mentions = ctx.message.mentions
    if not mentions:
        await ctx.send('Please mention member(s) to kill with an \'@\'')
        return
    for member in mentions:
        if member.name == 'GM' and not ctx.message.author == 'GM#2372':
            await ctx.send('Please do not attempt to murder my creator.')
            return
    if len(mentions)>=2:
        killed ='Congrats. '
        for member in mentions[0:-2]:
            killed += f'{member}'
        killed +=f'{mentions[-2]} and {mentions[-1]} have been killed.'
    else:
        if(ctx.message.author == f'{mentions[0].name}#{mentions[0].discriminator}'):
            killed = f'Congrats. {mentions[0]} has committed suicide.'
        else:
            killed = f'Congrats. {mentions[0]} has been killed'

    await ctx.send(killed)

    

bot.run(TOKEN)
