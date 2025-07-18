# Triggerwarden

[invite link](https://discord.com/oauth2/authorize?client_id=1347130542717403156)

triggerwarden is a discord bot that connects to the nationstates sse api and sends a notification when a trigger updates.

### supports
- region triggers
- nation triggers
- population triggers (user/role whitelist only, contact Ducky on discord or ducky4life@duck.com)
- influence triggers (same as pop triggers)
- banject activity (for ejection spotting in sieges)

it can also print out warning messages for liberations as a bonus

the bot restarts every 6 hours, so if it's down, wait a bit or message Ducky. shouldn't be down at update though.

## host it yourself!

population triggers is whitelist only because it hammers the api until stopped using my useragent instead of just requesting a sse endpoint. host the bot yourself to bypass the restriction!

### steps (Python)

make sure you have [python](https://www.python.org/downloads/) installed. create a discord bot in https://discord.com/developers/applications, click regenerate token in the bot tab to copy and save it, and enable message content intent

1. clone the repository
   ```
   git clone https://github.com/ducky4life/Triggerwarden.git
   ```
2. move to directory
   ```
   cd Triggerwarden
   ```
3. install dependencies
   ```
   pip install -r requirements.txt
   ```
4. create .env file
   ```
   touch .env
   ```
5. put your secrets in the .env file (without the brackets: [ ])
   ```
   USERAGENT="[your main nation name]"
   NS_TOKEN="[your bot token]"
   POPULATION_ALLOWED_USERS="[user ids seperated by commas]"
   POPULATION_ALLOWED_ROLES="[role ids seperated by commas]"
   SPAM_CHANNEL=[a channel id for the bot to send a message every time it sends an API request]
   ```
6. run trigger.py
   ```
   py trigger.py
   ```

### steps (Docker)

make sure you have [docker](https://www.docker.com) installed. create a discord bot in https://discord.com/developers/applications, click regenerate token in the bot tab to copy and save it, and enable message content intent

> [!IMPORTANT]
> you might have to change the first line in Dockerfile: `FROM --platform=linux/arm64/v8 arm64v8/python:3.11-slim` to `FROM python:3.11-slim` if you are using amd64 archetecture

1. clone the repository
   ```
   git clone https://github.com/ducky4life/Triggerwarden.git
   ```
2. move to directory
   ```
   cd Triggerwarden
   ```
3. create .env file
   ```
   touch .env
   ```
4. put your secrets in the .env file (without the brackets: [ ])
   ```
   USERAGENT="[your main nation name]"
   NS_TOKEN="[your bot token]"
   POPULATION_ALLOWED_USERS="[user ids seperated by commas]"
   POPULATION_ALLOWED_ROLES="[role ids seperated by commas]"
   SPAM_CHANNEL=[a channel id for the bot to send a message every time it sends an API request]
   ```
5. build the container
   ```
   docker build -t triggerwarden:latest -f Dockerfile .
   ```
6. run the container
   ```
   docker run --name triggerwarden triggerwarden:latest
   ```