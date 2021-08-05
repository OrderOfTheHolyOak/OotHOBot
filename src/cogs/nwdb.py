import requests
import discord
from discord.ext import commands
from urllib.parse import quote

class nwdb(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def nwdb(self, ctx, *, search : str):
    base_url = "https://nwdb.info/db"
    url = f"{base_url}/search/{quote(search)}.json"

    response = requests.get(url).json()
    data = response['data']

    count = len(data)
    
    embed = discord.Embed(
      title = f"{count} search result(s) for \"{search}\":",
      description = f"[NWDB](https://nwdb.info/) aims to bring you the most comprehensive database for New World.",
      colour = discord.Colour.green()
    )

    embed.set_thumbnail(url="https://nwdb.info/images/brand/logo_transparent_48.png")

    if count > 0:
      items = []
      for item in data:
        item_name = item['name']
        item_id = item['id']
        items.append(f"[{item_name}]({base_url}/item/{item_id}) \n")
      embed.add_field(
        name = "Results:",
        value = "".join(items)
      )

      await ctx.send(embed = embed)
    else:
      embed.colour = discord.Colour.red()

def setup(bot):
  bot.add_cog(nwdb(bot))