import requests
import discord
from discord.ext import commands
from urllib.parse import quote_plus

class wiki(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def wiki(self, ctx, *, search : str):
    url = f"https://newworld.fandom.com/wiki/{search.title().replace(' ', '_')}"
    msg = f"Found a page for {search}!\n{url}"

    response = requests.get(url)
    if response.status_code != 200:
      url = f"https://newworld.fandom.com/wiki/Special:Search?query={quote_plus(search)}&scope=internal&navigationSearch=true"
      msg = f"Didn't find a page for {search}\nBut here's a link to the wiki's search instead!\n<{url}>"

    await ctx.send(msg)

def setup(bot):
  bot.add_cog(wiki(bot))