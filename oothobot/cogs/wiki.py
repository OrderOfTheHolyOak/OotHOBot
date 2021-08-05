import requests
import discord
from discord.ext import commands
from urllib.parse import quote_plus

class wiki(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def wiki(self, ctx, *, search : str):
    response = requests.get(f"https://newworld.fandom.com/wiki/{search.title().replace(' ', '_')}")

    if response.status_code == 200:
      url = f"https://newworld.fandom.com/wiki/{search.title().replace(' ', '_')}"
    else:
      url = f"https://newworld.fandom.com/wiki/Special:Search?query={quote_plus(search)}&scope=internal&navigationSearch=true"

    await ctx.send(f"You searched for \"{search}\"\n{url}")

def setup(bot):
  bot.add_cog(wiki(bot))