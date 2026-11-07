from sqlalchemy import create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import asyncio
import tracemalloc
import discord
from discord import Message
from discord.ext import commands

from env import *


if not TOKEN:
    print("Set TOKEN environment varibale")
    exit(1)

if not CHANNEL_ID:
    print("Please set CHANNEL_ID environment varibale")
    exit(1)


tracemalloc.start()


# engine = create_engine('sqlite://database/bot.db')

# Create instance of Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# Command Dipatcher
COMMANDS = {}
def command(func, command: str | None = None):
    command = command or func.__name__
    COMMANDS[command] = func
async def dispatch_command(ctx, content):
    command, args = content[1:].split(" ")
    callback = COMMANDS.get(command)
    if not callback: return
    await callback(ctx, *args)
# End of Command Dispatcher


@command
async def test(ctx, *args):
    arguments = ', '.join(args)
    await ctx.send(f'{len(args)} arguments: {arguments}')


# Command Handler
@client.event
async def on_message(message: Message):
    content = message.content
    if content.startswith("$"):
        await dispatch_command(message.channel, content)


# on ready start event of warnings and error

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')



# main on connect event 
@client.event 
async def on_connect():

    await asyncio.sleep(5)
    channel = client.get_channel(CHANNEL_ID)
    await wish(channel)

# recursive function of checking date for wishes
async def wish(channel): 
    today = datetime.now()    
    today = str(today.strftime("%m-%d"))
    if today == "11-05":
        print("Artizote Birthday")
        await channel.send("@ghostor._. kya nakli id banaty ho drift")


# bot.add_command(test)

client.run(TOKEN)
   
