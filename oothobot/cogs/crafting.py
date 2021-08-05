import discord
from discord.ext import commands
import json

#https://newworldforge.com/database/crafting-recipes

resource_data = {}
resource_data_file = "oothobot/data/resources/list.json"

with open(resource_data_file) as file:
  resource_data = json.load(file)

class crafting(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  @commands.command()
  async def crafting(self, ctx, *, requested_item: str = None):
    if requested_item is None:
      embed = get_crafting_help()
      await ctx.send(embed=embed)
      return
    
    msg = ""
    match_found = False

    for index, (key, value) in enumerate(resource_data.items()):
      for index2, (key2, value2) in enumerate(value.items()):
        if key2.lower() == requested_item.lower():
          match_found = True
          msg = f'To get {value2["creates_amount"]} {value2["name"]}, you need:\n'
          requirements = []
          for requirement in value2["required_materials"]:
            amount = requirement["required_amount"]
            material = requirement["material"]
            requirements.append(f" `{amount} {material}`")
          
          msg = msg + "\n".join(requirements)
          await ctx.send(f"{msg}")
    
    if not match_found:
      await ctx.send(f"Could not find {requested_item}.")
    

def get_crafting_help():
  embed = discord.Embed(
    title="Crafting help",
    description=
    "You must provide a crafting type and a resource\n eg: `?crafting leatherworking \"raw hide\"`",
    colour=discord.Colour.orange()
  )

  embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/871708787319377960/871866810436317184/oak-tree-18-962642.png")

  return embed


def setup(bot):
  bot.add_cog(crafting(bot))