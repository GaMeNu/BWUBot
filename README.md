# BWUBot
Python bot for the Build With Us discord server. It sucks btw.

When using code from this repo, please make sure it stays Open-Source, and credit me or link this original repo with github.com/GaMeNu/BWUBot. Thank you :)

## Included commands:

**+help:** Take a guess.

**+on?:** Sends a message if the bot is on, along with time since it connected to the server

Aliases: +status, +a?

**+tips:** Sends a random anxiety tip, @V0C4L01D's idea

**+someone [message]:** Pings a random person in the server with the message.

Requires MOD rank (set in the .env.)

**+rickroll [message including user mention(s)]: ** Sends a rickroll in a DM to mentioned user(s)

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
