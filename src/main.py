import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# from utils.keep_alive import keep_alive
# keep_alive()


intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.reactions = True


command_prefix = "?"
description = "Order of the Holy Oak Discord Bot"


bot = commands.Bot(
  command_prefix = command_prefix,
  description = description,
  intents = intents
)


cogs: list = [
  "cogs.music",
  "cogs.online",
  "cogs.newbuild",
  "cogs.roles",
  "cogs.crafting",
  "cogs.wiki",
  "cogs.nwdb"
]


@bot.event
async def  on_ready():
  await bot.change_presence(activity=discord.Game(name="Stand tall, stand green!"))

  for cog in cogs:
    try:
      print(f"Loading cog {cog}")
      bot.load_extension(cog)
      print(f"Loaded cog {cog}")
    except Exception as e:
      exc = "{}: {}".format(type(e).__name__, e)
      print("Failed to load cog {}\n{}".format(cog, exc))

@bot.command()
async def ping(ctx):
    await ctx.send('**pong**')


token = ""

try:
  token = os.getenv('TOKEN')
except:
  print("No token found... Please input token")
  token = input("TOKEN: ")
  print(f"Using token {token}")

bot.run(token)