import os
import discord
import youtube_dl
from discord.ext import commands

from utils.ytdl import YTDLSource

class music(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def play(self, ctx, url : str):
    async with ctx.typing():
      if not url.startswith("https://youtube.com/") and not url.startswith("https://www.youtube.com/"):
        await ctx.send("Please only provide YouTube URLs")
        return

      if os.path.exists("song.webm"):
        os.remove("song.webm")
    
      try:
        await YTDLSource.from_url(url, loop=self.bot.loop)
      except youtube_dl.utils.DownloadError:
        await ctx.send("YouTube video not found")
        return

      voice_channel = ctx.author.voice.channel

      try:
        await voice_channel.connect()
      except:
        await ctx.send("Unable to join VC - Do I have permission?")
        return

      for file in os.listdir("./"):
        if file.endswith(".webm"):
          os.rename(file, "song.webm")

      voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
      
      voice.play(discord.FFmpegPCMAudio("song.webm"))

  @commands.command()
  async def leave(self, ctx):
    voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not currently connected to a voice channel.")

  @commands.command()
  async def pause(self, ctx):
    voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("No audio is currently playing.")

  @commands.command()
  async def resume(self, ctx):
    voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")

  @commands.command()
  async def stop(self, ctx):
    voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    else:
        await ctx.send("No audio is currently playing.")

def setup(bot):
  bot.add_cog(music(bot))