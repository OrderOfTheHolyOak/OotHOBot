import json
import atexit
import discord
from discord.ext import commands

reaction_roles = {}
excluded_roles = {}
available_roles = {}

reaction_roles_file = "src/data/roles/reaction.json"
excluded_roles_file = "src/data/roles/excluded.json"
available_roles_file = "src/data/roles/available.json"


class roles(commands.Cog):
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
    guild_id = str(ctx.guild.id)
    msg = ""
    if not guild_id in available_roles:
      available_roles[guild_id] = {}
    for category in available_roles[guild_id]:
      msg += f"**{category}**:\n"
      for role in available_roles[guild_id][category]:
        msg += f"**·** {role['emote']} {role['name']} \n"
      msg += "\n"
    await ctx.send(msg)

  @commands.command()
  async def add_category(self, ctx, *, category_name: str):
    guild_id = str(ctx.guild.id)
    if not guild_id in available_roles:
      available_roles[guild_id] = {}
    if not str(category_name) in available_roles[guild_id]:
      available_roles[guild_id][str(category_name)] = []
      await ctx.send(f"Added {category_name} to roles list.")
      store_available_roles()
    else:
      await ctx.send(f"The {category_name} category already exists")

  @commands.command()
  async def add_role_to_category(self, ctx, category_name: str, emote, role: discord.Role):
    guild_id = str(ctx.guild.id)
    if not guild_id in available_roles:
      available_roles[guild_id] = {}
    if not str(category_name) in available_roles[guild_id]:
      available_roles[guild_id][str(category_name)] = []
    role_name, role_emote = self.add_available_role(guild_id, category_name, emote, role)
    await ctx.send(f"Added {role_emote} {role_name} to {category_name}")

  @commands.command()
  async def remove_category(self, ctx, *, category_name: str):
    guild_id = str(ctx.guild.id)
    categories = available_roles.get(guild_id, None)
    embed = discord.Embed(
      title = f"Remove category **{category_name}** and **all roles within**?",
      colour = discord.Colours.red()
    )
    if categories is None:
      embed.description = "Couldn't find category."
    else:
      embed.description = "If you really want to do this, react with 🗑️"
      roles = []
      for role in categories[category_name]:
        roles.append(f"{role['emote']} {role['name']}")
      if len(roles) > 0:
        embed.add_field(
          name = "You're about to delete these available roles:",
          value = ", ".join(roles)
        )
      msg = await ctx.send(embed=embed)
      await msg.add_reaction("🗑️")

      def check(reaction, user):
        return (
          reaction.message.id == msg.id
          and user == ctx.message.author
          and str(reaction.emoji) == "🗑️"
        )

      await self.bot.wait_for("reaction_add", check=check)
      categories.pop(category_name)
      available_roles[guild_id] = categories
      store_available_roles()
      embed = discord.Embed(title=f"Category **{category_name}** and all roles within deleted")
      await ctx.send(embed=embed)

  @commands.command()
  async def remove_role_from_category(self, ctx, category_name: str, role_name: str):
    guild_id = str(ctx.guild.id)
    categories = available_roles.get(guild_id, None)
    embed = discord.Embed(
      title = f"Remove role **{role_name}** from category **{category_name}**",
      colour = discord.Colours.red()
    )
    if categories is None:
      embed.description = "Couldn't find category."
    else:
      roles = categories[category_name]
      if roles is None:
        embed.description = "Couldn't find role."
      else:
        embed.description = "If you really want to do this, react with 🗑️"
        for i in range(len(roles)):
          if roles[i]['name'] == role_name:
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("🗑️")

            def check(reaction, user):
              return (
                reaction.message.id == msg.id
                and user == ctx.message.author
                and str(reaction.emoji) == "🗑️"
              )

            await self.bot.wait_for("reaction_add", check=check)
            roles.pop(i)
        store_available_roles()
        embed = discord.Embed(title=f"Role **{role_name}** deleted from category **{category_name}**")
        await ctx.send(embed=embed)

  @commands.command()
  async def make_role_selection_post(self, ctx):
    guild_id = str(ctx.guild.id)
    embed = discord.Embed(
      title = "Set your role",
      description = "Use the reacions below to setup your role in this company.\nEach role is represented by a reaction.\nSee below for a full list of roles and their associated reaction.",
      colour = discord.Colour.green()
    )
    for category in available_roles[guild_id]:
      roles_array = []
      for role in available_roles[guild_id][category]:
        roles_array.append(f"{role['emote']} {role['name']}")

      embed.add_field(
        name = f"**{category}**:",
        value = "\n".join(roles_array)
      )
    post = await ctx.send(embed=embed)
    for category in available_roles[guild_id]:
      roles_array = []
      for role in available_roles[guild_id][category]:
        await post.add_reaction(role["emote"])


  #####################
  #      Events       #
  #####################

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    role, user = self.parse_reaction_payload(payload)
    if role is not None and user is not None:
      await user.add_roles(role, reason="rolebot")


  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
    role, user = self.parse_reaction_payload(payload)
    if role is not None and user is not None:
      await user.remove_roles(role, reason="rolebot")


  #####################
  #     Functions     #
  #####################

  def add_available_role(self, guild_id, category_name, emote, role: discord.Role):
    if not guild_id in available_roles:
      available_roles[guild_id] = {}
    if not str(category_name) in available_roles[guild_id]:
      available_roles[guild_id][str(category_name)] = []
    available_roles[guild_id][str(category_name)].append({
      "emote": emote,
      "role_id": role.id,
      "name": role.name
    })
    store_available_roles()
    return role.name, emote

  def parse_reaction_payload(self, payload: discord.RawReactionActionEvent):
    emoji = str(payload.emoji)
    user_id = payload.user_id
    guild_id = payload.guild_id
    guild = self.bot.get_guild(guild_id)
    user = guild.get_member(user_id)
    role = None
    if user_id != self.bot.user.id:
      categories = available_roles[guild_id]
      for category in categories:
        for available_role in categories[category]:
          emote = available_role['emote']
          if emoji == emote:
            role = guild.get_role(available_role['role_id'])
    return role, user

def setup(bot):
  bot.add_cog(roles(bot))




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