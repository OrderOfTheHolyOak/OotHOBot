import json
import atexit
import discord
from discord.ext import commands

settings = {}
settings_file = "src/data/settings/settings.json"

commands_list = {}
commands_file = "src/data/commands/commands.json"
admin_commands_list = {}
admin_commands_file = "src/data/commands/admin_commands.json"

class helper(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def set_admin_channel(self, ctx):
    guild_id = check_file(ctx)
    channel_id = ctx.channel.id
    try:
      settings[guild_id]["admin_channel"] = channel_id
      store_settings()
      await ctx.send(f"Thanks, {ctx.channel.name} is now your admin bot commands channel")
    except:
      await ctx.send("Something went wrong, please notify a developer")

  @commands.command()
  async def help(self, ctx, help_command: str = None):
    guild_id = check_file(ctx)
    try:
      admin_channel = str(settings[guild_id]["admin_channel"])
    except:
      await ctx.send("Please setup the admin channel first with `set_admin_channel` in the admin bot commands channel.")
    channel_id = str(ctx.channel.id)

    if help_command is not None:
      search_list = None
      if channel_id == admin_channel:
        search_list = {**commands_list, **admin_commands_list}
      else:
        search_list = commands_list.items()
      msg = None
      for bot_cog in search_list:
        for command in search_list[bot_cog]:
          if command['command'] == help_command:
            if len(command['params']) > 0:
              msg = f"***Example usage for {help_command}:***\n"
              msg += f"`{self.bot.command_prefix}{command['example']}`"
            else:
              await ctx.send(f"There are no parameters for the `{help_command}` command.")
              return
      if msg is not None:
        await ctx.send(msg)
      else:
        await ctx.send(f"Command not found: `{help_command}`")

    else:
      embed = discord.Embed(
        title = "Order of the Holy Oak bot help",
        descripion = "Below is a list of commands you can use in this channel",
        color = discord.Colour.orange()
      )

      commands_list_msg = ""
      for bot_cog in commands_list:
        commands_list_msg += f"\n_**{bot_cog}:**_\n"
        for command in commands_list[bot_cog]:
          params = ""
          if len(command['params']) > 0:
            for param in command['params']:
              params += f" <{param}>"
          commands_list_msg += f"**{self.bot.command_prefix}{command['command']} {params}:** {command['description']}\n"

      embed.add_field(name="Commands", value=commands_list_msg, inline = False)

      if channel_id == admin_channel:
        admin_commands_list_msg = ""
        for bot_cog in admin_commands_list:
          admin_commands_list_msg += f"\n_**{bot_cog}:**_\n"
          for command in admin_commands_list[bot_cog]:
            params = ""
            if len(command['params']) > 0:
              for param in command['params']:
                params += f" <{param}>"
            admin_commands_list_msg += f"**{self.bot.command_prefix}{command['command']} {params}:** {command['description']}\n"
        embed.add_field(name="Admin commands", value=admin_commands_list_msg, inline = False)

      embed.add_field(name="Extra information", value=f"Some commands require parameters, for some examples please use:\n`{self.bot.command_prefix}help <command_name>`")

      await ctx.send(embed = embed)

try:
  with open(settings_file) as file:
    settings = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(settings_file, "w") as file:
    json.dump({}, file)

try:
  with open(commands_file) as file:
    commands_list = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(commands_file, "w") as file:
    json.dump({}, file)

try:
  with open(admin_commands_file) as file:
    admin_commands_list = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
  with open(admin_commands_file, "w") as file:
    json.dump({}, file)

def check_file(ctx):
  guild_id = str(ctx.guild.id)
  if not guild_id in settings:
    settings[guild_id] = {}
  return guild_id

########################
#     Save on Exit     #
########################

@atexit.register
def store_settings():
  with open(settings_file, "w") as file:
    json.dump(settings, file)

def setup(bot):
  bot.add_cog(helper(bot))