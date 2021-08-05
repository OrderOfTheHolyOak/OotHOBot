import discord
from discord.utils import get
from discord.ext import commands
import json
import atexit
import os

available_roles = {}
reaction_roles = {}
excluded_roles = {}

available_roles_file = "src/data/roles/available.json"
reaction_roles_file = "src/data/roles/reaction.json"
excluded_roles_file = "src/data/roles/excluded.json"


# Used to keep track of current role assignments
try:
  with open(reaction_roles_file) as file:
    reaction_roles = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(reaction_roles_file, "w") as file:
    json.dump({}, file)

@atexit.register
def store_reaction_roles():
  with open(reaction_roles_file, "w") as file:
    json.dump(reaction_roles, file)

# Used for keeping bot in sync with server.
try:
  with open(available_roles_file) as file:
    available_roles = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(available_roles_file, "w") as file:
    json.dump({}, file)

@atexit.register
def store_available_roles():
  with open(available_roles_file, "w") as file:
    json.dump(available_roles, file)

# Used to keep track of excluded roles.
try:
  with open(excluded_roles_file) as file:
    excluded_roles = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(excluded_roles_file, "w") as file:
    json.dump({}, file)

@atexit.register
def store_excluded_roles():
  with open(excluded_roles_file, "w") as file:
    json.dump(excluded_roles, file)


class roles(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def roles(self, ctx):
    roles = ctx.author.roles

    roles_array = []
    for role in roles:
      if role.name != "@everyone":
        roles_array.append(role.name)

    string = "`, `".join(roles_array)
    await ctx.send(f"You have these roles: `{string}`")

  @commands.command()
  async def create_message(self, ctx):
    guild_id = ctx.guild.id
    available_roles_array = []

    for role in available_roles[str(guild_id)]:
      available_roles_array.append(f'{role["reaction_emoji"]} {role["name"]}')

    embed = discord.Embed(
      title = "Set your role",
      description = "Use the reacions below to setup your role in this company.\nEach role is represented by a reaction.\nSee below for a full list of roles and their associated reaction.",
      colour = discord.Colour.green()
    )

    embed.add_field(
      name = "Available Roles:",
      value = "\n".join(available_roles_array)
    )
    message = await ctx.send(embed=embed)

    for role in available_roles[str(guild_id)]:
      self.add_reaction(ctx.guild.id, role["reaction_emoji"], role["id"], ctx.channel.id, message.id)
      await message.add_reaction(role["reaction_emoji"])

  @commands.command()
  async def dump_server_roles(self, ctx):
    guild_id = ctx.guild.id
    roles = ctx.guild.roles
    roles_array = []

    available_roles[str(guild_id)] = []

    for role in roles:
      role_is_excluded = False
      for item in excluded_roles[str(guild_id)]:
          if item["name"] == role.name:
            role_is_excluded = True

      if not role_is_excluded:
        roles_array.append(role)
        available_roles[str(guild_id)].append(
          json.dumps({
            "id": role.id,
            "name": role.name,
            "reaction_emoji": "",
            "is_custom_emoji": False
          })
        )
    store_available_roles()

  @commands.command()
  async def exclude_role(self, ctx, given_role : str):
    guild_id = ctx.guild.id
    server_roles = ctx.guild.roles

    if not str(guild_id) in excluded_roles:
      excluded_roles[str(guild_id)] = []

    role_is_already_excluded = False

    for role in server_roles:
      if role.name == given_role:
        for item in excluded_roles[str(guild_id)]:
          if item["name"] == given_role:
            role_is_already_excluded = True

        if not role_is_already_excluded:
          excluded_roles[str(guild_id)].append({
            "id": role.id,
            "name": role.name,
          })
          await ctx.send(f"Added {given_role} to exclusions list")

    store_excluded_roles()
  
  @commands.command()
  async def unexclude_role(self, ctx, given_role : str):
    guild_id = ctx.guild.id
    server_roles = ctx.guild.roles

    if not str(guild_id) in excluded_roles:
      excluded_roles[str(guild_id)] = []

    role_is_excluded = False

    for role in server_roles:
      if role.name == given_role:
        for item in excluded_roles[str(guild_id)]:
          if item["name"] == given_role:
            role_is_excluded = True

        index = 0

        if role_is_excluded:
          for index, item in enumerate(excluded_roles[str(guild_id)]):
            if item["name"] == given_role:
              break
            else:
              index = -1

          excluded_roles[str(guild_id)].pop(index)

          await ctx.send(f"Removed {given_role} from exclusions list")

    store_excluded_roles()

  @commands.command()
  async def excluded_roles(self, ctx):
    guild_id = ctx.guild.id
    if not str(guild_id) in excluded_roles:
      excluded_roles[str(guild_id)] = []
    
    excluded_roles_array = []

    for role in excluded_roles[str(guild_id)]:
      excluded_roles_array.append(role["name"])
    
    msg = "`, `".join(excluded_roles_array)

    await ctx.send(f"The excluded roles are: `{msg}`")

  @commands.command()
  async def available_roles(self, ctx):
    guild_id = ctx.guild.id
    if not str(guild_id) in available_roles:
      available_roles[str(guild_id)] = []
    
    available_roles_array = []

    for role in available_roles[str(guild_id)]:
      available_roles_array.append(f'{role["reaction_emoji"]} {role["name"]}')
    
    msg = ", ".join(available_roles_array)

    await ctx.send(f"The available roles are: {msg}")

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

  @commands.has_permissions(manage_channels=True)
  @commands.command()
  async def reaction(
    self,
    ctx,
    emote,
    role: discord.Role,
    channel: discord.TextChannel,
    title,
    message,
  ):
    embed = discord.Embed(title=title, description=message)
    msg = await channel.send(embed=embed)
    await msg.add_reaction(emote)
    self.add_reaction(ctx.guild.id, emote, role.id, channel.id, msg.id)

  @commands.has_permissions(manage_channels=True)
  @commands.command()
  async def reaction_add(
    self, ctx, emote, role: discord.Role, channel: discord.TextChannel, message_id
  ):
    # self.add_reaction(ctx.guild.id, emote, role.id, channel.id, message_id)
    message = await channel.fetch_message(message_id)
    await message.add_reaction(emote)

  @commands.has_permissions(manage_channels=True)
  @commands.command()
  async def reactions(self, ctx):
    guild_id = ctx.guild.id
    data = reaction_roles.get(str(guild_id), None)
    embed = discord.Embed(title="Reaction Roles")
    if data is None:
      embed.description = "There are no reaction roles set up right now."
    else:
      for index, rr in enumerate(data):
        emote = rr.get("emote")
        role_id = rr.get("roleID")
        role = ctx.guild.get_role(role_id)
        channel_id = rr.get("channelID")
        message_id = rr.get("messageID")
        embed.add_field(
          name=f"{emote} - @{role}",
          value=f"ID: {index} - [message](https://www.discordapp.com/channels/{guild_id}/{channel_id}/{message_id})",
          inline=False,
        )
    await ctx.send(embed=embed)

  @commands.has_permissions(manage_channels=True)
  @commands.command()
  async def reaction_remove(self, ctx, index: int):
    guild_id = ctx.guild.id
    data = reaction_roles.get(str(guild_id), None)
    embed = discord.Embed(title=f"Remove Reaction Role {index}")
    rr = None
    if data is None:
      embed.description = "Given Reaction Role was not found."
    else:
      embed.description = (
        "Do you wish to remove the reaction role below? Please react with 🗑️."
      )
      rr = data[index]
      emote = rr.get("emote")
      role_id = rr.get("roleID")
      role = ctx.guild.get_role(role_id)
      channel_id = rr.get("channelID")
      message_id = rr.get("messageID")
      _id = rr.get("id")
      embed.set_footer(text=_id)
      embed.add_field(
        name=index,
        value=f"{emote} - @{role} - [message](https://www.discordapp.com/channels/{guild_id}/{channel_id}/{message_id})",
        inline=False,
      )
      msg = await ctx.send(embed=embed)
      if rr is not None:
        await msg.add_reaction("🗑️")

      def check(reaction, user):
        return (
          reaction.message.id == msg.id
          and user == ctx.message.author
          and str(reaction.emoji) == "🗑️"
        )

      reaction, user = await self.bot.wait_for("reaction_add", check=check)
      data.remove(rr)
      reaction_roles[str(guild_id)] = data
      store_reaction_roles()

  def add_reaction(self, guild_id, emote, role_id, channel_id, message_id):
    if not str(guild_id) in reaction_roles:
      reaction_roles[str(guild_id)] = []
    reaction_roles[str(guild_id)].append(
      {
        "emote": emote,
        "roleID": role_id,
        "channelID": channel_id,
        "messageID": message_id,
      }
    )
    store_reaction_roles()

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
  bot.add_cog(roles(bot))