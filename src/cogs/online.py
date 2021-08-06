import json
import atexit
import discord
from discord.ext import commands

opted_out = {}
opted_out_file = "src/data/online/optouts.json"

class online(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def online(self, ctx, *, role_name : str):
    roles = ctx.guild.roles
    guild_id = ctx.guild.id
    members_with_role: list = []
    online_members = []
    role_found = False
    if not str(guild_id) in opted_out:
      opted_out[str(guild_id)] = []
    for role in roles:
      if role.name.lower() == role_name.lower():
        role_found = True
        for role_member in role.members:
          if (role_member.status == discord.Status.online
            and role_member.id != ctx.author.id):
            members_with_role.append(role_member)
    if role_found == False:
      await ctx.send(f"Didn't find role \"{role_name}\"")
      return
    if len(members_with_role) > 0:
      message = f"Alerting {len(members_with_role)} online member(s) with \"{role_name}\" role.\n"
      for member in members_with_role:
        online_members.append(f"<@{member.id}>")
      message += ", ".join(online_members)
      await ctx.send(message)
    else:
      await ctx.send(f"There aren't any {role_name}s online right now.")

  @commands.command()
  async def dont_notify_me(self, ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    user_already_exists = False

    if not guild_id in opted_out:
      opted_out[guild_id] = []

    for opted_out_user in opted_out[guild_id]:
      if opted_out_user == user_id:
        user_already_exists = True

    if user_already_exists == True:
      await ctx.send("You already do not receive pings from the online command.")
    else:
      opted_out[guild_id].append(user_id)
      await ctx.send("You will no longer receive pings from the online command.")

  @commands.command()
  async def notify_me(self, ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    user_already_exists = False

    if not guild_id in opted_out:
      opted_out[guild_id] = []

    for opted_out_user in opted_out[guild_id]:
      if opted_out_user == user_id:
        user_already_exists = True

    if user_already_exists == False:
      await ctx.send("You already receive pings from the online command.")
    else:
      del opted_out[guild_id][opted_out[guild_id].index(user_id)]
      await ctx.send("You will now receive pings from the online command.")


def setup(bot):
  bot.add_cog(online(bot))



#######################
#     Setup Files     #
#######################

try:
  with open(opted_out_file) as file:
    opted_out = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(opted_out_file, "w") as file:
    json.dump({}, file)

########################
#     Save on Exit     #
########################

@atexit.register
def store_opted_out():
  with open(opted_out_file, "w") as file:
    json.dump(opted_out, file)