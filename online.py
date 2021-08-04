import discord
from discord.ext import commands

class online(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def online(self, ctx, role_name : str):
    members_with_role: list = []
    roles = ctx.guild.roles

    for role in roles:
      if role.name.lower() == role_name.lower():
        for role_member in role.members:
          if role_member.status == discord.Status.online:
            members_with_role.append(role_member)

    await ctx.send(f"Alerting {len(members_with_role)} online members with {role_name} role.")

    for member in members_with_role:
      await member.send(f"Hi {member.name}, {ctx.author.name} has pinged you by role in #{ctx.channel.name} in {ctx.guild.name}.\nThey're looking for an online {role_name} member to join them.")

def setup(bot):
  bot.add_cog(online(bot))