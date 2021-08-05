import discord
from discord.utils import get
from discord.ext import commands
import json
import atexit
import os

available_roles = {}
reaction_roles = {}
excluded_roles = {}

available_roles_file = "src/data/newroles/available.json"
reaction_roles_file = "src/data/newroles/reaction.json"
excluded_roles_file = "src/data/newroles/excluded.json"


class newroles(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  #####################
  #     Commands      #
  #####################

  @commands.command()
  async def roles(self, ctx):
    roles = ctx.author.roles

    roles_array = []
    for role in roles:
      if role.name != "@everyone":
        roles_array.append(role.name)

    string = "`, `".join(roles_array)
    await ctx.send(f"Hi <@{ctx.author.id}>, you have the following roles:\n`{string}`")

  @commands.command()
  async def available_roles(self, ctx):
    guild_id = ctx.guild.id
    msg = ""
    if not str(guild_id) in available_roles:
      available_roles[str(guild_id)] = {}
    for category in available_roles[str(guild_id)]:
      msg += f"**{category}**:\n"
      for role in available_roles[str(guild_id)][category]:
        msg += f"**·** {role['emote']} {role['name']} \n"
      msg += "\n"
    await ctx.send(msg)

  @commands.command()
  async def add_category(self, ctx, *, category_name: str):
    guild_id = ctx.guild.id
    if not str(guild_id) in available_roles:
      available_roles[str(guild_id)] = {}
    if not str(category_name) in available_roles[str(guild_id)]:
      available_roles[str(guild_id)][str(category_name)] = []
      await ctx.send(f"Added {category_name} to roles list.")
      store_available_roles()
    else:
      await ctx.send(f"The {category_name} category already exists")

  @commands.command()
  async def add_role_to_category(self, ctx, category_name: str, emote, role: discord.Role):
    guild_id = ctx.guild.id
    if not str(guild_id) in available_roles:
      available_roles[str(guild_id)] = {}
    if not str(category_name) in available_roles[str(guild_id)]:
      available_roles[str(guild_id)][str(category_name)] = []
    role_name, role_emote = self.add_available_role(guild_id, category_name, emote, role)
    await ctx.send(f"Added {role_emote} {role_name} to {category_name}")

  @commands.command()
  async def remove_category(self, ctx, *, category_name: str):
    guild_id = ctx.guild.id
    categories = available_roles.get(str(guild_id), None)
    embed = discord.Embed(title=f"Remove category {category_name} and all roles within?")
    category = None
    if categories is None:
      embed.description = "Couldn't find category."
    else:
      embed.description = "If you really want to do this, react with 🗑️"
      category = categories[category_name]
      roles = []
      for role in categories[category_name]:
        roles.append(f"{role['emote']} {role['name']}")
      if len(roles) > 0:
        embed.add_field(
          name = "You're about to delete these available roles:",
          value = ", ".join(roles)
        )
      msg = await ctx.send(embed=embed)
      if category is not None:
        await msg.add_reaction("🗑️")

      def check(reaction, user):
        return (
          reaction.message.id == msg.id
          and user == ctx.message.author
          and str(reaction.emoji) == "🗑️"
        )

      await self.bot.wait_for("reaction_add", check=check)
      categories.pop(category_name)
      available_roles[str(guild_id)] = categories
      store_available_roles()
      embed = discord.Embed(title=f"Category {category_name} and all roles within deleted")
      await ctx.send(embed=embed)

  #####################
  #      Events       #
  #####################

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    role, user = self.parse_reaction_payload(payload)
    if role is not None and user is not None and (payload.user_id != self.bot.user.id):
      await user.add_roles(role, reason="rolebot")


  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
    role, user = self.parse_reaction_payload(payload)
    if role is not None and user is not None and (payload.user_id != self.bot.user.id):
      await user.remove_roles(role, reason="rolebot")


  #####################
  #     Functions     #
  #####################

  def add_available_role(self, guild_id, category_name, emote, role: discord.Role):
    if not str(guild_id) in available_roles:
      available_roles[str(guild_id)] = {}
    if not str(category_name) in available_roles[str(guild_id)]:
      available_roles[str(guild_id)][str(category_name)] = []
    available_roles[str(guild_id)][str(category_name)].append({
      "emote": emote,
      "role_id": role.id,
      "name": role.name
    })
    store_available_roles()
    return role.name, emote

  def parse_reaction_payload(self, payload: discord.RawReactionActionEvent):
    guild_id = payload.guild_id
    data = reaction_roles.get(str(guild_id), None)
    if data is not None:
      for rr in data:
        emote = rr.get("emote")
        if payload.message_id == rr.get("messageID"):
          if payload.channel_id == rr.get("channelID"):
            if str(payload.emoji) == emote:
              guild = self.bot.get_guild(guild_id)
              role = guild.get_role(rr.get("roleID"))
              user = guild.get_member(payload.user_id)
              return role, user
    return None, None

def setup(bot):
  bot.add_cog(newroles(bot))




###################
#   Setup files   #
###################

try:
  with open(reaction_roles_file) as file:
    reaction_roles = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(reaction_roles_file, "w") as file:
    json.dump({}, file)

try:
  with open(available_roles_file) as file:
    available_roles = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(available_roles_file, "w") as file:
    json.dump({}, file)

try:
  with open(excluded_roles_file) as file:
    excluded_roles = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(excluded_roles_file, "w") as file:
    json.dump({}, file)

########################
#     Save on Exit     #
########################

@atexit.register
def store_reaction_roles():
  with open(reaction_roles_file, "w") as file:
    json.dump(reaction_roles, file)
@atexit.register


def store_available_roles():
  with open(available_roles_file, "w") as file:
    json.dump(available_roles, file)
@atexit.register


def store_excluded_roles():
  with open(excluded_roles_file, "w") as file:
    json.dump(excluded_roles, file)