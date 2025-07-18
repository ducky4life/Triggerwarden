import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import keep_alive
from dotenv import load_dotenv
import sans

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

useragent = str(os.getenv("USERAGENT"))
token = str(os.getenv("NS_TOKEN"))
sans.set_agent(f"Triggerwarden Discord bot by Ducky used by {useragent}")
client = commands.Bot(command_prefix=["!ns "], intents=intents)


async def send_codeblock(ctx, msg):
    if len(msg) > 1993:
        first_msg = msg[:1993]
        second_msg = msg[1993:].strip()
        await ctx.send(f"```{first_msg}```")
        await ctx.send(f"```{second_msg}```")
    else:
        await ctx.send(f"```{msg}```")


@client.event
async def on_ready():
    print('ready')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Who You Gonna Call?"))
    await client.tree.sync()



async def nation(nations, channel_id):
    async with sans.AsyncClient() as asyncclient:
        async for event in sans.serversent_events(asyncclient, "change").view(nations=nations):
            channel = await client.fetch_channel(channel_id)
            if "influence in" in event["str"]:
                await channel.send(event["str"])

async def region(regions, channel_id):
    async with sans.AsyncClient() as asyncclient:
        async for event in sans.serversent_events(asyncclient, "admin").view(regions=regions):
            channel = await client.fetch_channel(channel_id)
            if "updated." in event["str"]:
                await channel.send(event["str"])

async def banject(regions, channel_id):
    async with sans.AsyncClient() as asyncclient:
        async for event in sans.serversent_events(asyncclient, "eject").view(regions=regions):
            channel = await client.fetch_channel(channel_id)
            await channel.send(event["str"])



async def getpopulation(nation):
    request = sans.Nation(nation, "census", scale="3")
    root = sans.get(request).xml
    sans.indent(root)
    return(root[0][0][0].text)

async def population(nations, channel_id):
    channel = await client.fetch_channel(channel_id)
    spam_channel = await client.fetch_channel(int(os.getenv("SPAM_CHANNEL"))) # does not work without this

    for nation in nations:
        nation["population"] = await getpopulation(nation["name"])

    while nations != []:
        for nation in nations:
            if await getpopulation(nation["name"]) == nation["population"]:
                await spam_channel.send("hello getting population")
            else:
                await channel.send(f"Population of {nation['name']} has changed")
                nations.remove(nation)
    await channel.send("All nations have their population updated, stopping")
    asyncio.current_task().cancel()



async def getinfluence(nation):
    request = sans.Nation(nation, "census", scale="65")
    root = sans.get(request).xml
    sans.indent(root)
    return(root[0][0][0].text)

async def influence(nations, channel_id):
    channel = await client.fetch_channel(channel_id)
    spam_channel = await client.fetch_channel(int(os.getenv("SPAM_CHANNEL"))) # does not work without this

    for nation in nations:
        nation["influence"] = await getinfluence(nation["name"])

    while nations != []:
        for nation in nations:
            if await getinfluence(nation["name"]) == nation["influence"]:
                await spam_channel.send("hello getting influence")
            else:
                await channel.send(f"Influence of {nation['name']} has changed")
                nations.remove(nation)
    await channel.send("All nations have their influence updated, stopping")
    asyncio.current_task().cancel()





async def SSEtrigger(ctx, type:str, targets:str=None, channel:discord.TextChannel=None):
    target_list = targets.split(",")
    if channel == None:
        channel = ctx.channel

    if type == "nation":
        task = asyncio.create_task(nation(target_list, channel.id))
    elif type == "region":
        task = asyncio.create_task(region(target_list, channel.id))
    elif type == "banject":
        task = asyncio.create_task(banject(target_list, channel.id))

    class Buttons(discord.ui.View):
        @discord.ui.button(label='Stop SSE', style=discord.ButtonStyle.red)
        async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            task.cancel()
            await interaction.response.edit_message(content='SSE has been stopped', view=None)

    await ctx.send("Connected, click button to stop SSE",view=Buttons(timeout=None))


@client.hybrid_command(description="connect to sse with the changes bucket")
@app_commands.describe(nations="list of nations to track, separated by commas. do not put spaces after commas. e.g. 'nation1,nation2,nation3'", channel="what channel to send sse activities to")
async def nationtrigger(ctx, nations:str=None, channel:discord.TextChannel=None):
    await SSEtrigger(ctx, "nation", nations, channel)


@client.hybrid_command(description="connect to sse with the admin bucket")
@app_commands.describe(regions="list of nations to track, separated by commas. do not put spaces after commas. e.g. 'region1,region2,region3'", channel="what channel to send sse activities to")
async def regiontrigger(ctx, regions:str=None, channel:discord.TextChannel=None):
    await SSEtrigger(ctx, "region", regions, channel)


@client.hybrid_command(description="watch for banjects")
@app_commands.describe(regions="list of regions to track, separated by commas. do not put spaces after commas. e.g. 'region1,region2,region3'", channel="what channel to send sse activities to")
async def banjectactivity(ctx, regions:str=None, channel:discord.TextChannel=None):
    await SSEtrigger(ctx, "banject", regions, channel)




@client.hybrid_command(description="watch for population changes")
@app_commands.describe(nations="list of nations to track, separated by commas. do not put spaces after commas. e.g. 'nation1,nation2,nation3'", channel="what channel to send population updates to")
async def populationtrigger(ctx, nations:str=None, channel:discord.TextChannel=None):
    allowed_users = str(os.getenv("POPULATION_ALLOWED_USERS")).split(",")
    allowed_roles = str(os.getenv("POPULATION_ALLOWED_ROLES")).split(",")
    author_roles = [role.id for role in ctx.message.author.roles]

    allowed = False

    for role in allowed_roles:
        if int(role) in author_roles or str(ctx.message.author.id) in allowed_users:
            allowed = True

    if allowed == True:
        nation_list = nations.split(",")
        nation_dict = [{"name": nation} for nation in nation_list]
        task = asyncio.create_task(population(nation_dict, channel.id))

        class Buttons(discord.ui.View):
            @discord.ui.button(label='Stop API', style=discord.ButtonStyle.red)
            async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                task.cancel()
                await interaction.response.edit_message(content='Tracking has been stopped', view=None)

        await ctx.send("Connected to API, please remember to stop when done so Ducky doesn't spam the API",view=Buttons(timeout=None))
        
    else:
        await ctx.send("You do not have permission to use this command, please contact Ducky")



@client.hybrid_command(description="watch for influence changes")
@app_commands.describe(nations="list of nations to track, separated by commas. do not put spaces after commas. e.g. 'nation1,nation2,nation3'", channel="what channel to send influence updates to")
async def influencetrigger(ctx, nations:str=None, channel:discord.TextChannel=None):
    allowed_users = str(os.getenv("POPULATION_ALLOWED_USERS")).split(",")
    allowed_roles = str(os.getenv("POPULATION_ALLOWED_ROLES")).split(",")
    author_roles = [role.id for role in ctx.message.author.roles]

    allowed = False

    for role in allowed_roles:
        if int(role) in author_roles or str(ctx.message.author.id) in allowed_users:
            allowed = True

    if allowed == True:
        nation_list = nations.split(",")
        nation_dict = [{"name": nation} for nation in nation_list]
        task = asyncio.create_task(influence(nation_dict, channel.id))

        class Buttons(discord.ui.View):
            @discord.ui.button(label='Stop API', style=discord.ButtonStyle.red)
            async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                task.cancel()
                await interaction.response.edit_message(content='Tracking has been stopped', view=None)

        await ctx.send("Connected to API, please remember to stop when done so Ducky doesn't spam the API",view=Buttons(timeout=None))
        
    else:
        await ctx.send("You do not have permission to use this command, please contact Ducky")






@client.hybrid_command(description="sends liberation warning messages. please input links. supports m+e and fpm")
@app_commands.describe(moveplusendorse="m+e if yes", native="m+e target")
@app_commands.choices(moveplusendorse=[
    app_commands.Choice(name='m+e', value="m+e"),
    app_commands.Choice(name='no', value="no")
])
async def warningmessage(ctx, point=None, region=None, *, moveplusendorse="no", native=None):
    match moveplusendorse:
        case "no":
            ten = f"""<@&272392896806912000>
**__Ten Minute Warning.__**

Make sure you have prepared a World Assembly nation in our jump point, https://www.nationstates.net/region=artificial_solar_system

**Endorse this nation and __ALL__ the nations endorsing it: {point}**

The next ping will be a five minute warning."""
            
            five = f"""<@&272392896806912000>
**__Five Minute Warning__**
**DO NOT MOVE YET - PREPARE**

Our target region: {region} Have this page open.

**Make sure you have endorsed this nation and all nations endorsing it: {point}**

**DO NOT move until the move order is given.**
The next ping will be a two minute warning."""
            
            two = f"""<@&272392896806912000>
**__Two Minute Warning__**
**DO NOT MOVE YET - RADIO SILENCE - DO NOT SPEAK**

Our target region: {region} Have this page open.

**Make sure you have endorsed this nation and all nations endorsing it: {point}**

**__DO NOT MOVE YET__**

The next ping will be a movement order. **Be ready to move as fast as you can.** ***You will only have a few seconds***"""
            
            fpm = f"""<@&272392896806912000>
**__Two Minute Warning__**
**DO NOT MOVE YET - RADIO SILENCE - DO NOT SPEAK**

Our target region: {region} Have this page open.

**Make sure you have endorsed this nation and all nations endorsing it: {point}**

Our cross has moved now, **do not follow.**

**__DO NOT MOVE YET__**

The next ping will be a movement order. **Be ready to move as fast as you can.** ***You will only have a few seconds***"""
            
            go = "<@&272392896806912000> GO GO GO"
        
        case "m+e":
            ten = f"""<@&272392896806912000>
**__Ten Minute Warning.__**

Make sure you have prepared a World Assembly nation in our jump point, https://www.nationstates.net/region=artificial_solar_system

**Endorse this nation and __ALL__ the nations endorsing it: {point}**

The next ping will be a five minute warning."""
            
            five = f"""<@&272392896806912000>
**__Five Minute Warning__**
**DO NOT MOVE YET - PREPARE**

Our target region: {region} Have this page open.

**Make sure you have endorsed this nation and all nations endorsing it: {point}**

**After moving, we will immediately endorse {native}. ** Have this page open.

 **DO NOT move until the move order is given.**
The next ping will be a two minute warning."""

            two = f"""<@&272392896806912000>
**__Two Minute Warning__**
**DO NOT MOVE YET - RADIO SILENCE - DO NOT SPEAK**

Target region: {region} Have this page open and refresh it once now.

**Make sure you have endorsed this nation and all nations endorsing it: {point}**

**After moving, we will immediately endorse {native}. ** Have this page open and refresh it once now.

**__DO NOT MOVE YET__**

The next ping will be a movement order. **Be ready to move as fast as you can.** ***You will only have a few seconds***"""
            
            fpm = f"""<@&272392896806912000>
**__Two Minute Warning__**
**DO NOT MOVE YET - RADIO SILENCE - DO NOT SPEAK**

Target region: {region} Have this page open and refresh it once now.

**Make sure you have endorsed this nation and all nations endorsing it: {point}**

Our cross has moved now, **do not follow.**

**After moving, we will immediately endorse {native}. ** Have this page open and refresh it once now.

**__DO NOT MOVE YET__**

The next ping will be a movement order. **Be ready to move as fast as you can.** ***You will only have a few seconds***"""
            
            go = f"<@&272392896806912000> GO Endo {native}"

    await send_codeblock(ctx, ten)
    await send_codeblock(ctx, five)
    await send_codeblock(ctx, two)
    await ctx.send("fpm 2 minute warning:")
    await send_codeblock(ctx, fpm)
    await send_codeblock(ctx, go)



keep_alive.keep_alive()
client.run(token)
