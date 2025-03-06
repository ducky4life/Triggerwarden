import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import keep_alive
from dotenv import load_dotenv
import sans


intents = discord.Intents.all()
intents.members = True

load_dotenv()

token = os.getenv("NS_TOKEN")
sans.set_agent("Ducky")
client = commands.Bot(command_prefix=["!ns ", "!ns "], intents=intents)


@client.event
async def on_ready():
    print('ready')
    await client.tree.sync()



async def main(nations, channel_id):
    async with sans.AsyncClient() as asyncclient:
        async for event in sans.serversent_events(asyncclient, "change").view(nations=nations):
            channel = await client.fetch_channel(channel_id)
            await channel.send(event["str"])



@client.hybrid_command(description="connect to sse with the changes bucket")
@app_commands.describe(nations="list of nations to track, separated by commas. do not put spaces after commas. e.g. 'nation1,nation2,nation3'", channel="what channel to send sse activities to")
async def nationtrigger(ctx, nations:str=None, channel:discord.TextChannel=None):
    nation_list = nations.split(",")
    task = asyncio.create_task(main(nation_list, channel.id))

    class Buttons(discord.ui.View):
        @discord.ui.button(label='Stop SSE', style=discord.ButtonStyle.red)
        async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            task.cancel()
            await interaction.response.edit_message(content='SSE has been stopped', view=None)

    await ctx.send("Connected, click button to stop SSE",view=Buttons())



keep_alive.keep_alive()
client.run(token)