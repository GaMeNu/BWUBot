# BWUBot
Depricated Python bot for the Build With Us discord server. It sucks btw.

## Table of Contents:

[Setting up your own BWUBot instance](https://github.com/GaMeNu/BWUBot/blob/main/README.md#set-up-your-own-bwubot-instance)

[Available commands](https://github.com/GaMeNu/BWUBot/blob/main/README.md#included-commands)

## Set up your own BWUBot instance:

### Required packages:
`pip install discord.py`

`pip install discord-py-interactions`

`pip install pytz`

`pip install python-dateutil`

`pip install python-dotenv`

`pip install pynput`

`pip install pywin32`

(Run these commands from your terminal)

### .env config:
```
BWU_DISCORD_TOKEN = [Bot's token goes here]
DISCORD_GUILD= [Your server's name goes here]
DISCORD_COMMANDS_CHANNEL = [The commands channel ID goes here]
MOD_ROLE_ID= [The ID of the Mod role in your server goes here]
CREATOR_ID = [Your own ID goes here (gives you protection within kill system)]
BWU_BOTDATA_PATH = [The FULL path of your "botdata.json" file goes here. Format: C:/Users/.../botdata.json]
```

### Required discord premissions:
**Required bot intents:**
![image](https://user-images.githubusercontent.com/98153342/196023145-addb686b-e412-428f-b4d1-108ae4229a50.png)

**URL Generator permissions:**
![image](https://user-images.githubusercontent.com/98153342/196023198-91e89132-697b-4d85-a6ae-ddbe9cf4185a.png)
Use the generated URL (at the bottom of the pag) to invite the bot into your server.


## Included commands:

**+help:** Take a guess.

**+on?:** Sends a message if the bot is on, along with time since it connected to the server

Aliases: +status, +a?

**+tips:** Sends a random anxiety tip, @V0C4L01D's idea

**+someone [message]:** Pings a random person in the server with the message.

Requires MOD rank (set in the .env.)

**+rickroll [message including user mention(s)]:** Sends a rickroll in a DM to mentioned user(s)

**+insult [<none>/noun/custom/adj]:** Sends a random insult, chooses from a specific list if specified.



### Timezone system:
**+tz:** Sends a link to a list of all valid timezones. Link: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568

**+tz set <timezone>:** Sets your timezone, Case-Sensitive

**+tz get <User mention(s)>:** Gets a user current time. Requires both you and the user to have registered your timezones. 

### Kill system:
**+kill [message including user mention(s)]:** Kills the mentioned user(s) if they are alive.

Aliases: +liquidate, +destroy, +stab, +attack, +shoot, +assassinate

**+revive [message including user mention(s)]:** Revives the mentioned user(s) if they are dead.

**+terrorism:** Randomly kills 0-12 server members.

Aliases: +bomb

**+dead:** Sends a list of all dead members.

**+alive:** Sends a list of all alive members.

**+alive? [Message including a user(s) mention]:** Sends a list of all members mentioned, checking if they are alive.

Aliases: +isAlive
