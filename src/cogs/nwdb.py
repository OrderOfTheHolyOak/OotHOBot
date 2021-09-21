import requests
import discord
from discord.ext import commands
from urllib.parse import quote

rarity_colours = {
  "0": discord.Colour.darker_grey(),
  "1": discord.Colour.green(),
  "2": discord.Colour.blue(),
  "3": discord.Colour.purple(),
  "4": discord.Colour.orange()
}

class nwdb(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def nwdb(self, ctx, *, search : str):
    base_url = "https://nwdb.info/db"
    url = f"{base_url}/search/{quote(search)}"

    response = requests.get(url).json()
    data = response['data']

    count = len(data)
    
    embed = discord.Embed(
      title = f"{count} search result(s) for \"{search}\":",
      description = f"[NWDB](https://nwdb.info/) aims to bring you the most comprehensive database for New World.",
    )

    embed.set_thumbnail(url="https://nwdb.info/images/brand/logo_transparent_48.png")

    if count > 0:
      items = []
      for item in data:
        item_name = item['name']
        item_id = item['id']
        items.append(f"[{item_name}]({base_url}/item/{item_id}) \n")

      if count > 10:
        items = items[:10]

      embed.add_field(
        name = "Results:",
        value = "".join(items)
      )

      if count == 1:
        embed.colour = rarity_colours[str(item['rarity'])]

      if count > len(items):
        text = f"[here]({base_url})"
        embed.add_field(
          name = "Search results limited",
          value = f"Only the first 10 results were shown. Click {text} and search via the website."
        )

      await ctx.send(embed = embed)
    else:
      embed.colour = discord.Colour.red()

def setup(bot):
  bot.add_cog(nwdb(bot))