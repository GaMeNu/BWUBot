import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
from asyncore import loop
import os
from dotenv import load_dotenv
import time as t
import random as rand
import json
import logging
import datetime
import pytz
from datetime import timezone
from dateutil import tz
from dateutil.zoneinfo import get_zonefile_instance
import win32gui as win
from pynput import keyboard


#Why am I still even updating the GitHub

#All .env tokens, required for the bot to function without any modifications.
load_dotenv()
TOKEN = os.getenv('BWU_DISCORD_TOKEN')
GUILD = int(os.getenv('DISCORD_GUILD'))
try:
    NSFW_CHANNEL = int(os.getenv('DISCORD_NSFW_CHANNEL'))
    ALERT_CHANNEL = int(os.getenv('DISCORD_ALERT_CHANNEL'))
except:
    logging.warning('No NSFW Channel or NSFW Alert channel found! Proceeding without these...')
    NSFW_CHANNEL = 0
    ALERT_CHANNEL = 0
COMMANDS_CHANNEL = int(os.getenv('DISCORD_COMMANDS_CHANNEL'))
MOD_ROLE = int(os.getenv('MOD_ROLE_ID'))
CREATOR= int(os.getenv('CREATOR_ID'))
BOTDATA = os.getenv('BWU_BOTDATA_PATH')

logging.getLogger().setLevel(logging.DEBUG)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)
bot.remove_command('help')

def create_botdata_entry(member_id):
    global botdata
    id_str = str(member_id)
    botdata[id_str] = {}
    logging.info(f'[Botdata] created new botdata entry for userID {member_id}, name = {guild.get_member(member_id)}')
    

def remove_botdata_entry(member_id):
    global botdata
    id_str = str(member_id)
    try:
        del botdata[id_str]
        logging.info(f'[Botdata] deleted botdata entry for userID {member_id}, name = {guild.get_member(member_id)}')
    except:
        logging.error(f'[Botdata] error while deleting botdata entry for userID {member_id}, are you sure they exist?')


def choose_random_member():
    guild = discord.utils.find(lambda g: g.id == GUILD, bot.guilds)
    members = guild.members
    return rand.choice(members)


def reset_vars():
    global dead_members
    dead_members=[]
    global suicide_times
    suicide_times={}
    global uptime
    uptime=0

    global skyOffline
    skyOffline = False

    global guild
    guild = discord.utils.find(lambda g: g.id == GUILD, bot.guilds)
    
    global creator
    creator = guild.get_member(CREATOR)

    global botdata

    try:
        with open(BOTDATA,'r') as f:
            botdata = json.loads(f.read())

    except:
        logging.critical('[VARSET] Error while loading from JSON! Recreating JSON file.')
        botdata = {}
        for member in guild.members:
            create_botdata_entry(member.id)
    else:
        botdata_temp = botdata
        for member in guild.members:
            if not str(member.id) in botdata.keys():
                create_botdata_entry(member.id)
        
        for memberID in list(botdata.keys()):
            member = guild.get_member(int(memberID))
            if member == None:
                remove_botdata_entry(int(memberID))
                
                
            


    
    with open(BOTDATA,'w') as f:
        f.write(json.dumps(botdata))
            


#Time since connection established loop
@tasks.loop(seconds=1)
async def time_connected_loop():
    global uptime
    #How the hell do presences work
    #the update loop itself
    uptime+=1
    if (uptime%60==0):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f'for +help; Online for {uptime//60} minutes.',details=f'Hello world!'))


#Prints some data to terminal, also sends connected msg on COMMANDS_CHANNEL
@bot.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.id == GUILD, bot.guilds)
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in guild {guild.name}, ID: {guild.id}')
    members = f'\n - '.join([f'[{str(member.status).upper()}] {member.name}, ID = {member.id}' for member in guild.members])
    print(f'{len(guild.members)} Members on the server:\n - {members}')
    cmds_ch = bot.get_channel(COMMANDS_CHANNEL)

    activity = discord.Activity(type=discord.ActivityType.watching, name='for +help')
    await bot.change_presence(activity=activity)
    await cmds_ch.send(f'Connected to server!\nWatching for **+help**...')
    reset_vars()

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name='for +help; Online for 0 minutes.',state='Existing',details=f'Hello world!'))
    time_connected_loop.start()
    logging.info("[TCL] Started uptime loop!")

@bot.event
async def on_resumed():
    time_connected_loop.restart()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.channel.send("Error: Command not found you dumdum! Try using **+help**.")
    return


@bot.event
async def on_member_join(member):
   create_botdata_entry(member.id)


@bot.event
async def on_member_remove(member):
    remove_botdata_entry(member.id)


#detects if a message was sent in NSFW_CHANNEL, and sends a "spotted" alert in ALERTS_CHANNEL
@bot.event
async def on_message(message):
    global skyOffline
    global creator


    if (message.author==bot.user):
        return

    if (message.channel.id==NSFW_CHANNEL):
        alerts = bot.get_channel(ALERT_CHANNEL)
        await alerts.send(f'{message.author} was spotted in the NSFW channel!!!')

    skyMember = guild.get_member(694247027172966481)
    if (skyOffline) and (message.author == skyMember):
        await message.channel.send(f'{creator.mention}, Sky\'s back!')
        print('\a')
        skyOffline = False
    
    async def userMsgContainsWord(userID:int, word:str):
        if ((f' {word} ' in message.content.lower()) or (f'{word} ' in message.content.lower()) or (f' {word}' in message.content.lower()) or (word == message.content.lower())) and (message.author.id == userID):
            await message.channel.send(f"Stop with the {word}!", reference=message)
        
    await userMsgContainsWord(skyMember.id, 'gj')
    await userMsgContainsWord(skyMember.id, 'goodjob')
    await userMsgContainsWord(creator.id, 'kk')
    


    
    
    if message.content.lower() == 'wow':
        if rand.randrange(1, 5)==1:
            await message.channel.send('<:wow:1028426222704807937>',reference=message)
    
    await bot.process_commands(message)

#help command, pretty basic embed.
@bot.command()
async def help(ctx):
    embed_color=rand.randrange(1, 16777216)
    help_embed = discord.Embed(title="BWUBot help", description="Here you can find all currently available commands!",color=embed_color,timestamp=datetime.datetime.utcnow(),url='https://github.com/GaMeNu/BWUBot')
    help_embed.set_footer(text=f'GitHub: https://github.com/GaMeNu/BWUBot ??? Help message color: {hex(embed_color)}')
    help_embed.set_author(name='GameMenu (GM)\'s')
    help_embed.add_field(name="+help",value="Guess what this one does, I bet you can't.", inline=False)
    help_embed.add_field(name="+on?",value="Also works with: +status, +a?\nSends a response if the bot is on, along with the time it's been connected",inline=False)
    help_embed.add_field(name='+tips',value='Sends a random anxiety tip.\nCommand idea and sources by V0C4L01D.',inline=False)
    help_embed.add_field(name='+tz [get/set/<none>]', value='Set your own timezone or get someone else\'s current time.',inline=False)
    help_embed.add_field(name='+about', value='Sends some info about BWUBot.',inline=False)
    help_embed.add_field(name="+rickroll [Message including a user(s) mention]",value="Rickrolls the mentioned users in DMs.",inline=False)
    help_embed.add_field(name='+insult [noun/adj/custom/<none>] [Message including a user(s) mention]', value = 'Insults the mentioned user(s).',inline=False)
    help_embed.add_field(name='+someone [message]',value='Pings a random person in the server with the message.\nRequires MOD rank.',inline=False)
    help_embed.add_field(name="+kill [(Message including a user(s) mention)/(*/all)]",value="Also works with:+liquidate, +destroy, +stab, +attack, +shoot, +assassinate\nKills the alive user(s) mentioned in the message, */all = everyone",inline=False)
    help_embed.add_field(name="+revive [(Message including a user(s) mention)/(*/all)]",value="Revives the dead user(s) mentioned in the message, */all = everyone",inline=False)
    help_embed.add_field(name='+terrorism',value="Also works with: +bomb\nKills 0-12 random people.")
    help_embed.add_field(name="+dead",value="Sends a list of all dead members.",inline=False)
    help_embed.add_field(name="+alive",value="Sends a list of all alive members.",inline=False)
    help_embed.add_field(name="+alive? [Message including a user(s) mention]",value="Also works with: +isAlive\nSends a list of all members mentioned, checking if they are alive.",inline=False)


    await ctx.channel.send(embed=help_embed)

@bot.command()
async def tz(ctx, *args):
    if not args:
        await ctx.send('List of available timezones can be found in this link:\nhttps://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568')
        return


    if args[0] == 'set':
        if len(args)==1:
            await ctx.send('Error: Incorrect syntax!\nUsage: +tz set (timezone)\nLink to a list of all timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568')
            return
        if not args[1] in list(get_zonefile_instance().zones):
            await ctx.send('Error: Timezone not found! Please note that timezones are Case-Sensitive.\nLink to a list of all timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568')
            return
        authorID = str(ctx.author.id)
        botdata[authorID]['timezone']=args[1]
        with open(BOTDATA,'w') as f:
            f.write(json.dumps(botdata))
        await ctx.send(f'Successfully set your timezone to {args[1]}!')


    elif args[0] == 'get':
        authorID = str(ctx.author.id)
        if (not 'timezone' in botdata[authorID].keys()) or botdata[authorID]['timezone'] == "":
            await ctx.send('Error: You must register your own timezone before accessing others\'!\nPlease use `+tz` to get a list of all valid timezones, and `+tz set <timezone>` to set your timezone.')
            return
        
        mentions = ctx.message.mentions
        if not mentions:
            await ctx.send("Error: No user mentions supplied!")
            return
        
        msg =''
        for member in mentions:
            if str(botdata[str(member.id)]['timezone']) != "":
                member_tz=pytz.timezone(str(botdata[str(member.id)]['timezone']))
                msg += f'For **{member}**, it is currently **{datetime.datetime.now(member_tz).strftime("%X %p, %A %b %d, %Y** (Timezone: %Z, UTC%z)")}\n'
        

        await ctx.send(msg)

    else:
        await ctx.send('Error: Invalid argument! Usage: +tz (get/set/<null>)')



@bot.command()
async def skyOff(ctx):
    global skyOffline
    skyOffline = True
    await ctx.send('Sky is now offline!')


@bot.command()
async def about(ctx):
    await ctx.send('Oh, about me?')
    t.sleep(3)
    await ctx.send('I was created in September 2022 as GameMenu\'s hobby project.')
    t.sleep(1)
    await ctx.send('(Probably the best program he\'ll ever write as well lmao)')
    t.sleep(3)
    await ctx.send('Anyway use `+help` to look at all available commands.')


@bot.command()
async def randnum(ctx,*args):
    min = 1
    max = 7
    if args:
        if len(args)>=2:
            try:
                min = int(args[0])
                max = int(args[1])+1
            except:
                await ctx.send('Error: One of the 2 provided arguments could not be parsed!')
                return
        else:
            try:
                max = int(args[0])+1
            except:
                await ctx.send('Error: The provided argument could not be parsed!')
                return
    await ctx.send(f'Rolled {rand.randrange(min,max)}! (Range: {min}..{max-1})')





@bot.command()
async def rickroll(ctx,args):
    mentions = ctx.message.mentions
    if not mentions:
        await ctx.channel.send("Error: No mentions supplied!")
        return
    
    creator = ctx.guild.get_member(CREATOR)
    
    for member in mentions:
        if not member == creator:
            await member.send(f":musical_note: Never gonna give you up!\nNever gonna let you down!\nNever gonna run around and desert you!\n\nNever gonna make you cry!\nNever gonna say goodbye\nNever gonna tell a lie, or hurt you! :notes:\n\n- Sent by {ctx.message.author}")
        else:
            await ctx.send('Skipping my creator...')
    

@bot.command()
async def insult(ctx,*args):
    mentions = ctx.message.mentions
    if not mentions:
        await ctx.send("Error: No mentions supplied!")
        return
    

    """ 
    #Code for creator saftey from insults.
    #You wanna turn it on, you coward?

    creator = ctx.guild.get_member(CREATOR)

    if creator in mentions and not ctx.author==creator:
        mentions.remove(creator)
    
    if not mentions:
        await ctx.send("Error: No mentions supplied! (My creator cannot be insulted.)")
        return 
    """

    def insult(insult: str, insulted: list, type: str):
        msg = ''
        if len(insulted)==1:
            if type == 'noun':
                msg += f'{mentions[0]}, you really are '
                if insult[0] in ['a','e','i','o','u','A','E','I','O','U']:
                    msg +='an '
                else:
                    msg+='a '
                msg+= f'{insult}'
            elif type == 'adj':
                msg += f'{mentions[0]}, you really are '
                msg+= f'{insult}'
            elif type == 'custom':
                msg = f'{mentions[0]}, {insult}'
            else:
                logging.error('Incorrect argument provided for insult(type)! Must be either noun, adj, or custom! Continuing with arg custom...')
                msg = insult(insult, insulted, 'custom')
        else:
            for member in mentions:
                msg+=f'{member}, '
            if type == 'noun':
                msg += f'you all are {insult}'
                if msg[-1] == 's':
                    msg += 'es'
                else:
                    msg += 's'
            elif type == 'adj':
                msg += f'you all are {insult}'
            elif type == 'custom':
                msg += f'{insult}'
            else:
                logging.error('Incorrect argument provided for insult(type)! Must be either noun, adj, or custom! Continuing with arg custom...')
                msg = insult(insult, insulted, 'custom')
        msg += '!'
        return msg


    insults_noun = [
        'airy-fairy',
        'ankle-biter',
        'arsehole',
        'arse-licker',
        'arsemonger',
        'barmy',
        'bell-end',
        'berk',
        'bitch',
        'chav',
        'cheese-eating surrender monkey',
        'chuffer',
        'dingus',
        'gannet',
        'git',
        'knob',
        'knob-head',
        'lazy sod',
        'ligger',
        'maggot',
        'mingebag',
        'minger',
        'muppet',
        'naff',
        'ninny',
        'nutter',
        'pikey',
        'pillock',
        'piss-off',
        'plonker',
        'prat',
        'scrubber',
        'skiver',
        'stupid fuck',
        'slag',
        'tosser',
        'trollop',
        'twit',
        'uphill gardener',
        'wanker',
        'wazzock',
    ]
    insults_adj = [
        'crude steel',
        'daft as a bush',
        'daft cow',
        'dead from the neck up',
        'dodgy',
        'gone to the dogs',
        'gormless',
        'like a dog with two dicks',
        'manky',
        'mad as a bag of ferrets',
        'not batting on a full wicket',
        'one sandwich short of a picnic',
        'plug-Ugly'
        ]
    insults_custom =[
        'fuck you',
        'you suck',
        'no one ever liked you, and no one will like you',
        'evolution\'s mistake was wasting over 20,000 years of developing humans just to create you'
    ]

    if not args:
        insults_all = []
        insults_all.extend(insults_noun)
        insults_all.extend(insults_adj)
        insults_all.extend(insults_custom)
        rand_insult = rand.choice(insults_all)
        if rand_insult in insults_noun:
            msg = insult(rand_insult, mentions, 'noun')

        elif rand_insult in insults_adj:
            msg = insult(rand_insult, mentions, 'adj')
        else:
            msg = insult(rand_insult, mentions, 'custom')


    if args[0]=='noun':
        msg = insult(rand.choice(insults_noun), mentions, 'noun')
    elif args[0] in ['adj','adjective']:
        msg = insult(rand.choice(insults_adj), mentions, 'adj')
    elif args[0] == 'custom':
        msg = insult(rand.choice(insults_custom), mentions, 'custom')
    else:
        insults_all = []
        insults_all.extend(insults_noun)
        insults_all.extend(insults_adj)
        insults_all.extend(insults_custom)
        rand_insult = rand.choice(insults_all)
        if rand_insult in insults_noun:
            msg = insult(rand_insult, mentions, 'noun')
        elif rand_insult in insults_adj:
            msg = insult(rand_insult, mentions, 'adj')
        else:
            msg = insult(rand_insult, mentions, 'custom')


    await ctx.send(msg)

    
    

@bot.command()
async def someone(ctx, *args):
    
    pinger = ctx.message.author
    if not discord.utils.get(pinger.roles, id=MOD_ROLE):
        await ctx.channel.send('Error: You do not have premission!')
        return
    
    
    pinged = choose_random_member()
    msg = f'{pinged.mention} '
    msg += ' '.join(args)
    msg += f'\n - Pinged by {ctx.message.author}'
    await ctx.channel.send(msg)




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
    global uptime
    uptimeS = uptime%60
    uptimeM = (uptime//60)%60
    uptimeH = uptime//3600
    await ctx.send(f"Hello world! I am currently online.\nTime since connected: {uptimeH}:{uptimeM}:{uptimeS}")


def send_chat(out: str):
    keyboard.press('t')
    t.sleep(0.1)
    keyboard.release('t')
    t.sleep(0.1)
    keyboard.type(out)


@bot.command()
async def GM(ctx, *args):
    if not 'Minecraft' in (win.GetWindowText(win.GetForegroundWindow())):
        await ctx.send('Error: GM is not currently playing Minecraft!')
        return

    
    if not args:
        await ctx.send('Error: No arguments supplied!')
        return
    
    
    if args[0] == 'say':
        msg = ctx.message.content[len('+GM say ')::]
        send_chat(msg)
        







#Kill command, will go into more detail in the command
@bot.command(aliases = ['liquidate','destroy','stab','attack','shoot','assassinate'])
async def kill(ctx, *args):
    #Collects all mentions in message. If no mentions found returns a sort of error.

    
    mentions = ctx.message.mentions
    if not mentions:
        if ((not args) or (not args[0] in ['all','*'])):
            await ctx.send('Please mention member(s) to kill with an \'@\', or kill everyone with \'*\'')
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

    if args[0] in ['all','*']:

        killed = 'Mass murder! Killed:\n'

        guild = discord.utils.find(lambda g: g.id == GUILD, bot.guilds)
        count =0
        for member in guild.members:
            if (not member in dead_members) and (not f'{member.name}#{member.discriminator}' == 'GM#2372') and (not member.bot):
                killed += f'- {member}\n'
                dead_members.append(member)
                count+=1
        
        killed += f'{count} members were killed overall.'
    

    else:
        killed =''
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
                    suicide_times[member] = 1
                else:
                    killed += f'{mentions[0]} has been killed.'
            else:
                if(f'{ctx.message.author.name}#{ctx.message.author.discriminator}' == f'{mentions[0].name}#{mentions[0].discriminator}'):
                    
                    times_did = suicide_times[member]
                    
                    if times_did==1:
                        killed +=f'{mentions[0]} has committed suicide. AGAIN.'
                    elif times_did==2:
                        killed += f'{mentions[0]} has committed suicide for the third time!'
                    elif times_did==3:
                        killed += f'Please stop killing yourself...'
                    elif times_did == 4:
                        killed += f'Do you need help?'
                    elif times_did==6:
                        killed += f'There are better ways to go about this then repeatedly committing suicide...'
                    elif times_did==7:
                        killed += f'Life has so much to offer!'
                    elif times_did==8:
                        killed += f'{mentions[0]} you good?'
                    elif times_did==9:
                        killed += f'Hi, GM here. Idk how you feel, but if something is wrong, please, please contact actual resources. This bot is a joke, not something to be taken seriously, and it\'s definitely not a good source. So please refer to actual resources if you need to.\n-GM'
                    elif times_did>=10 and times_did<20:
                        killed += f'{mentions[0]} has committed suicide.'
                    elif times_did == 20:
                        killed+=f'**Achivement get: Dedicated to Death!**\nKill yourself 20 times using +stab'
                    elif times_did>20 and times_did<50:
                        killed += f'{mentions[0]} has committed suicide.'
                    elif times_did==50:
                        killed += f'There\'s nothing here but blood...'
                    elif times_did==51:
                        killed+=f'Blood... So much blood...'
                    elif times_did==52:
                        killed+='Why... Why are you still here?'
                    elif times_did==53:
                        killed+='Are you really that dedicated? Are you hunting for easter eggs?'
                    elif times_did==54:
                        killed+='Or are you just suicidal?'
                    elif times_did==55:
                        killed+='In the case of the latter, please contact actual sources... This bot is not a good source.'
                    elif times_did==56:
                        killed+='I guess I\'m gonna leave you to it...'
                    elif times_did>56:
                        killed+=' * NO RESPONSE'
                    
                    suicide_times[member] += 1
                else:
                    killed += f'{mentions[0]} was already dead.'

    await ctx.send(killed)


@bot.command()
async def revive(ctx,*args):

    #Kinda works like +kill, except the opposite for the checks with dead_members.
    mentions = ctx.message.mentions
    if not mentions:
        if ((not args) or (not args[0] in ['all','*'])):
            await ctx.send('Please mention member(s) to kill with an \'@\', or kill everyone with \'*\'')
            return
    for member in mentions:
        if member.name == 'GM' and not f'{ctx.message.author.name}#{ctx.message.author.discriminator}' == 'GM#2372':
            await ctx.send('As well as the intentions were, my creator is immune to murder and thus cannot be revived.')
            return
        if member.bot:
            await ctx.send('Bots are immune to murder.')
            return

    if args[0] in ['all','*']:

        revived = 'The ressurection has come! Revived:\n'

        guild = discord.utils.find(lambda g: g.id == GUILD, bot.guilds)
        count = 0
        for member in guild.members:
            if member in dead_members:
                revived += f'- {member}\n'
                dead_members.remove(member)
                count+=1
        
        revived += f'{count} members were revived overall.'
            
    else:
        revived = ''
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
                    revived += f'{mentions[0]} has somehow revived himself even though they were already alive...?'
                else:
                    revived += f'{mentions[0]} is not dead.'

    await ctx.channel.send(revived)


@bot.command(aliases=["bomb"])
async def terrorism(ctx):
    guild = discord.utils.find(lambda g: g.id == GUILD, bot.guilds)
    members=guild.members
    modifier = rand.choice([0.5,1,2.5])
    num_killed=rand.randrange(1,6)

    killed = "What? A bombing has been carried out!\n"
    num_killed=int(num_killed*modifier)

    if modifier == 0.5:
        killed += rand.choice(["It happened in the middle of nowhere!","It happened in an abandoned channel.","Chat was already dead tho..."])
    elif modifier == 2.5:
        killed += rand.choice(["They bombed a BUS!","It happened in the middle of the city!","The police didn't show up in time!"])
    else:
        killed+=rand.choice(["They threw a granade in the middle of town! Most people ran away."])
    killed += "\n"
    if num_killed == 0:
        killed+= "No one was killed."
    elif len(dead_members)==len(members):
        killed+="Alas, the server is already a graveyard! No one was killed."
    
    else:
        killed += "**Killed:**\n"
        dead_count = 0
        for i in range (num_killed):
            member = rand.choice(members)
            while((member in dead_members and not len(dead_members)==len(members))):
                member = rand.choice(members)
            
            if not len(dead_members)==len(members):
                dead_members.append(member)
                killed += f" - {member}\n"
                dead_count+=1
        if dead_count == 1:
            killed += f'1 person was killed overall.'
        else:
            killed += f"{dead_count} people were killed overall."
    killed +='\n'
    
    killed += '(Note: Please **do not actually commit terrorism IRL**. I think this is pretty clear.)'
    


    await ctx.channel.send(killed)
        
    

    
#Sends a list of all members in dead_members
@bot.command()
async def dead(ctx):
    dead = "Dead members (L):\n"
    for member in dead_members:
        dead+=f'- {member}\n'
    dead+= f"{len(dead_members)} member(s) are dead overall"
    await ctx.send(dead)


@bot.command()
async def alive(ctx):
    guild = discord.utils.find(lambda g: g.id == GUILD, bot.guilds)
    members=guild.members
    ret_msg = "Alive members (Big W):\n"
    count = 0
    for member in members:
        if not member in dead_members:
            ret_msg+=f' - {member}\n'
            count+=1
    ret_msg+=f'{count} members are alive overall.'

    await ctx.channel.send(ret_msg)



@bot.command(name='alive?',aliases=['isAlive'])
async def isAlive(ctx):
    mentions = ctx.message.mentions

    if not mentions:
        await ctx.send('Please mention member(s) to check with an \'@\'')
        return
    
    return_msg='Dead check:\n'
    for member in mentions:
        return_msg+=f'{member} - '
        if member in dead_members:
            return_msg+='DEAD'
        else:
            return_msg+='ALIVE'
        return_msg+='\n'
    await ctx.channel.send(return_msg)


    




@bot.command()
#this was wender_159's idea, not mine.
#please help me
async def uwu(ctx):
    await ctx.send('\"UwU\"')
    

bot.run(TOKEN)
