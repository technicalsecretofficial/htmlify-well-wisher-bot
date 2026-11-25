from sqlalchemy.orm import Session
import tracemalloc
import discord
from discord.ext import commands
from env import *
from database.models.user import User
from database.models import engine
from time import sleep
from utils import *
import os


for rdir in ["generated"]:
    if not os.path.exists(rdir):
        os.mkdir(rdir)

if not TOKEN:
    print("Set TOKEN environment varibale")
    exit(1)

if not CHANNEL_ID:
    print("Please set CHANNEL_ID environment varibale")
    exit(1)


tracemalloc.start()

# Create instance of Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

session = Session(engine)

bot = commands.Bot(command_prefix='$', intents=intents)


#CRUD OPERATION commands

# add birthday
@bot.hybrid_command()
async def add(ctx, date: str = "",*, full_name: str = ""):
        try:     
            sanitized_name = sanitize_name(full_name)
            sanitized_date = sanitize_date(date)

            if not sanitized_date:
                await ctx.send("Write Date in Correct Format MM-DD")
                return

            if not sanitized_name:
                await ctx.send("Enter name correctly.")
                return

            if sanitized_name and sanitized_date:
                await ctx.send(f"date: {sanitized_date} , full_name: {sanitized_name}") 
                new_user = User(full_name=sanitized_name, date_of_birth=sanitized_date)
                session.add(new_user)
                session.commit()
        except:
            await ctx.send("Write Date and full Name Correctly")


#fetch birthday
@bot.hybrid_command()
async def fetch(ctx):
    users = session.query(User).all()
    users_html = generate_template("users-table.html", users=users)
    tmp_url = htmlify_tmpfile(users_html)
    await ctx.send("Here is the exported birthday list:\n" + tmp_url)

#get user 
@bot.hybrid_command()
async def find(ctx:commands.Context, arg: str):

    if sanitized_date := sanitize_date(arg):
        users = session.query(User).filter_by(date_of_birth =sanitized_date).all()
        users = session.query(User).all()
        for user in users:
            sleep(0.1)
            await ctx.send(user.to_json_snippet())
    
    elif sanitized_name := sanitize_name(arg):
        users = session.query(User).filter_by(full_name=sanitized_name).all()
        users = session.query(User).filter_by(date_of_birth =sanitized_date).all()
        users = session.query(User).all()
        for user in users:
            sleep(0.1)
            await ctx.send(user.to_json_snippet())

    else:
        await ctx.send("Wrong argument couldn't find anyone.")


#Update User
@bot.hybrid_command()
async def update(ctx:commands.Context,id:str , *, arg:str):
    
    s_id = sanitize_id(id)

    if not s_id:
        await ctx.send("ID is not valid.")
        return
    
    user = session.query(User).filter_by(id=s_id).first()
    
    if not user:
        await ctx.send("Record not found with this ID.")
        return
    
    if sanitized_date := sanitize_date(arg):
        user.date_of_birth = sanitized_date
        session.commit()
        await ctx.send("Updated User Info successfully.")

    elif sanitized_name := sanitize_name(arg):
        user.full_name = sanitized_name
        session.commit()
        await ctx.send("Updated User Info successfully.")

    else:
        await ctx.send("Wrong argument couldn't find anyone.")


#delete User
@bot.hybrid_command()
async def delete(ctx:commands.Context,id: str):
    

    s_id = sanitize_id(id)
    user = session.query(User).filter_by(id=s_id).first() if s_id else False
    if user:
        session.delete(user)
        session.commit()
        await ctx.send(f" {user.full_name} deleted successfully.")
    else:
        await ctx.send(f" Wrong No User found")


# on ready start event of warnings and error
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')



# run bot and client

bot.run(TOKEN)

client.run(TOKEN)
   
