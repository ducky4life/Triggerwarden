# Triggerwarden

[invite link](https://discord.com/oauth2/authorize?client_id=1347130542717403156)

triggerwarden is a discord bot that connects to the nationstates sse api and sends a notification when a trigger updates.

### supports
- region triggers
- nation triggers
- population triggers (user/role whitelist only, contact Ducky on discord or ducky4life@duck.com)

it can also print out warning messages for liberations as a bonus

the bot restarts every 6 hours, so if it's down, wait a bit or message Ducky. shouldn't be down at update though.

## host it yourself!

population triggers is whitelist only because it hammers the api until stopped using my useragent instead of just requesting a sse endpoint. host the bot yourself to bypass the restriction!

### steps

make sure you have [python](https://www.python.org/downloads/) installed.

1. clone the repository
```
git clone https://github.com/ducky4life/triggerwarden.git
```
2. install dependencies
```
pip install -r requirements.txt
```
3. create .env file
```
touch .env
```
4. put your secrets in the .env file
   - `NS_TOKEN="[your bot token]"`
   - `POPULATION_ALLOWED_USERS="[user ids seperated by commas]"`
   - `POPULATION_ALLOWED_ROLES="[role ids seperated by commas]"`
   - `SPAM_CHANNEL=[a channel id for the bot to send a message every time it sends an API request]`

5. run trigger.py
```
py trigger.py
```
