import json
import atexit
import discord
from discord import role
from discord.ext import commands


builds = {}
builds_file = "src/data/build/builds.json"


class newbuild(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def build(self, ctx, role_or_weapon: str = None):
    check_file(ctx)
    guild_id = str(ctx.guild.id)
    if role_or_weapon is None or role_or_weapon == "":
      msg = f"You must provide a role or a weapon to the build command. (Replace spaces with hyphens) Example:\n"
      msg += "`build life-staff`"
      await ctx.send(msg)
      return
    builds_list = []
    for build_type in builds[guild_id]:
      if role_or_weapon == build_type:
        for build in builds[guild_id][build_type]:
          builds_list.append(build)
    if len(builds_list) > 0:
      embed = discord.Embed(
        title = f"{role_or_weapon} Builds",
        description = f"You'll find a list of all {role_or_weapon} builds below.",
        colour = discord.Colour.green()
      )
      for build in builds_list:
        embed.add_field(name = f"{build['name']}", value = f"**[{build['id']}]: ** {build['url']}")
      await ctx.send(embed = embed)
    else:
      await ctx.send(f"Didn't find any {role_or_weapon} builds :(")


  @commands.command()
  async def add_role_build(self, ctx, name: str = None, role: str = None, url: str = None):
    check_file(ctx)
    guild_id = str(ctx.guild.id)
    if (role is None or
      name is None or
      url is None):
      msg = "Usage: `add_role_build <build_name> <role_name> <url>`:\n"
      msg += "`add_role_build Best-PvE-Healer healer https://google.com`"
      await ctx.send(msg)
      return
    id = None
    all_builds = []
    for build_type in builds[guild_id]:
      for build in builds[guild_id][build_type]:
        all_builds.append(build)
    id = len(all_builds)
    build = {
      "role": role,
      "name": name,
      "url": url,
      "id": id
    }
    builds[guild_id][role].append(build)
    await ctx.send(f"Build \"{name}\" added to {role} builds")

  @commands.command()
  async def add_weapon_build(self, ctx, name: str = None, weapon: str = None, url: str = None):
    check_file(ctx)
    guild_id = str(ctx.guild.id)
    if (weapon is None or
      name is None or
      url is None):
      msg = "Usage: `add_weapon_build <build_name> <weapon_name> <url>`:\n"
      msg += "`add_weapon_build PvP-Healer-Beast life-staff https://google.com`"
      await ctx.send(msg)
      return
    id = None
    all_builds = []
    for build_type in builds[guild_id]:
      for build in builds[guild_id][build_type]:
        all_builds.append(build)
    id = len(all_builds)
    build = {
      "weapon": weapon,
      "name": name,
      "url": url,
      "id": id
    }
    builds[guild_id][weapon].append(build)
    await ctx.send(f"Build \"{name}\" added to {weapon} builds")

  @commands.command()
  async def show_all_builds(self, ctx):
    print("Nothing")

###################
#   Setup files   #
###################


try:
  with open(builds_file) as file:
    builds = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(builds_file, "w") as file:
    json.dump({}, file)

def check_file(ctx):
  guild_id = str(ctx.guild.id)
  if not guild_id in builds:
    builds[guild_id] = {}

########################
#     Save on Exit     #
########################

@atexit.register
def store_builds():
  with open(builds_file, "w") as file:
    json.dump(builds, file)


def setup(bot):
  bot.add_cog(newbuild(bot))