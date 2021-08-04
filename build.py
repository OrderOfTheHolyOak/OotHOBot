import discord
from discord.ext import commands

class build(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

#Main Menu of Gear Build
  @commands.command()
  async def build(self, ctx, role : str = None):

    embed = discord.Embed( 
      title = get_title(role),
      description = get_description(role),
      colour = get_colour(role)
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/871708787319377960/871866810436317184/oak-tree-18-962642.png")

    if role != None:
      embed.add_field(name="Description", value=f"This is the best recommended {role} build", inline=False)
      embed.add_field(name="Gear", value=get_recommended_gear_for_role(role), inline=False)
      embed.add_field(name="Skills", value=get_recommended_skills_for_role(role), inline=False)

    await ctx.send(embed=embed)

def get_recommended_gear_for_role(role):
  if (role == 'tank'):
    return "[Thicc Helmet](https://google.com), \n Breasts Plate, \r\n Metal Cock Sock"
  if (role == 'healer'):
    return "Cloth Robe, Life Stick"
  if (role == 'dps'):
    return "Stabby stab"

def get_recommended_skills_for_role(role):
  if (role == 'tank'):
    return "Smack, \n Taunt"
  if (role == 'healer'):
    return "Big Heal, \n Little Heal"
  if (role == 'dps'):
    return "Big stab, \n Little Stab"

def get_title(role = None):
  if (role == 'tank'):
    return "Tank Gear"
  if (role == 'healer'):
    return "Healer Gear"
  if (role == 'dps'):
    return "DPS Gear"

  return "Main page"

def get_description(role = None):
  if (role == 'tank'):
    return "This is where you'll find tanking gear"
  if (role == 'healer'):
    return "This is where you'll find healer gear"
  if (role == 'dps'):
    return "This is where you'll find DPS gear"

  return "You must provide a role to build, eg: `?build healer` \n Available roles: `dps`, `healer`, `tank`"

def get_colour(role = None):
  if (role == 'tank'):
    return discord.Colour.red()
  if (role == 'healer'):
    return discord.Colour.green()
  if (role == 'dps'):
    return discord.Colour.blue()

  return discord.Colour.orange()

def setup(bot):
  bot.add_cog(build(bot))