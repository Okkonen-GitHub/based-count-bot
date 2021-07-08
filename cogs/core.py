
import asyncio
import discord
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands import check
from discord.ext.commands import ExtensionError
from discord.ext.commands import Context

from datetime import datetime
from main import starttime

import psutil

import json
import os


def is_dev(ctx):
  with open(f"{os.path.dirname(__file__)}/config.json", "r") as f:
    conf = json.load(f)
  return str(ctx.author.id) in conf["devs"].values()

def byte_converter(mem: int):
  """Converts the number of bytes into human readable text"""
  symbols = ("KB", "MB", "GB")
  prefix = {}
  for i, str in enumerate(symbols):
    prefix[str] = 1 << (i + 1) * 10
  for string in reversed(symbols):
    if mem >= prefix[string]:
      value = float(mem) / prefix[string]
      return "%.1f%s" % (value, string)
  return "%sB" % mem

class Core(Cog):

  def __init__(self, bot) -> None:
    self.bot = bot
  
  @check(is_dev)
  @command(name='logout', aliases = ["shutdown"], hidden=True)
  async def _logout(self, ctx):
    await ctx.send("Shutdown in 3 seconds")
    from cogs.counter import DataBase
    DataBase().db.close()
    await asyncio.sleep(3)
    await self.bot.close()
    
  @command(name='info', aliases = ['i'], usage="b!help", description="Show information about the bot")
  async def _info(self, ctx: Context):
    current_time = datetime.now()
    embed = discord.Embed(color = 0xf235d9)
    ps = psutil.Process(os.getpid())
    embed.set_author(
      name="Bot info",
      icon_url=self.bot.user.avatar_url
    )
    embed.description = "This is a custom bot created by Okkonen#5411.\nIt is used to keep track of how many times people are called based.\n\nHow to use: `@some-user based`\n"
    embed.add_field(
      name="Current Ping:",
      value=f"{round(self.bot.latency * 1000, 1)} ms"
    )
    embed.add_field(
      name="Bot Uptime:",
      value=f"{str(starttime(current_time))[:-7]}"
    )
    embed.set_footer(
      text=f"CPU: {ps.cpu_percent()}/{psutil.cpu_percent()}% | RAM {byte_converter(ps.memory_full_info().rss)} ({round(ps.memory_percent(), 1)}%)",
      icon_url = "https://media.discordapp.net/attachments/514213558549217330/514345278669848597/8yx98C.gif"
    )
    await ctx.send(embed=embed)


  @command(name='ping', aliases = ['latency'], description="Show bot latency", usage="`b!ping`")
  async def _ping(self, ctx):
    await ctx.send(f"Current latency: {round(self.bot.latency * 1000, 1)} ms")

  @check(is_dev)
  @command(name="load", hidden=True, aliases = ["laod", "lext", "extl"])
  async def _load(self, ctx, ext):
    try:
      self.bot.load_extension(f"cogs.{ext}")
      await ctx.send(f"Loaded {ext}")
      return print(f"Loaded {ext}")
    except ExtensionError as err:
      await ctx.send(f"Failed to Load {ext} [{err}]")
      print(f"Failed to Load {ext} [{err}]")
  

  @check(is_dev)
  @command(name="unload", hidden=True, aliases = ["unlaod", "uext", "extu"])
  async def _unload(self, ctx, ext):
    try:
      self.bot.unload_extension(f"cogs.{ext}")
      await ctx.send(f"Unloaded {ext}")
    
    except ExtensionError as err:
      await ctx.send(f"Failed to unoad {ext} [{err}]")
      print(f"Failed to unoad {ext} [{err}]")
  
  @check(is_dev)
  @command(name='list_ext', aliases = ["extls", "ls", "lsext", "loaded", "list"], hidden=True)
  async def _list_ext(self, ctx):
    e = discord.Embed(color = 0xff5100)
    cogs = ""
    for i, cog in enumerate(self.bot.cogs, start=1):
      cogs += f"`{i}.`  {cog}\n"
    e.description = f"**These are the loaded cogs at the moment:**\n{cogs}"
    await ctx.send(embed = e)

  @check(is_dev)
  @command(name='reload', aliases = ["rext", "extr", "re"], hidden=True)
  async def _reload(self, ctx, ext = "all"):
    active_cogs = list(self.bot.cogs)
    e = discord.Embed(color=0xff5100)
    if ext == "all":
      for cog in active_cogs:
        try:
          self.bot.reload_extension(f"cogs.{cog.lower()}")
          e.add_field(name=f"Reloaded succesfully:", value=f"{cog}", inline=False)
        except ExtensionError as err:
          e.add_field(name=f"failed to reload [{err}]", value=f"{cog}", inline=False)
    else:
      try:
        self.bot.reload_extension(f"cogs.{ext}")
        e.add_field(name=f"Reloaded succesfully", value=f"{ext}", inline=False)
      except ExtensionError as err:
        e.add_field(name=f"failed to reload [{err}]", value=f"{ext}", inline=False)
    await ctx.send(embed = e)

  @command(hidden=True, aliases=["cmd", "commands", "command", "cmds"])
  async def help(self, ctx: Context, command: str = None):
    """Displays the help menu sorted by cog/class name."""

    async def add_reactions(message):
      """Add reactions in the background to speed things up."""
      for emoji_ in emojis: # loops through the emojis
        await message.add_reaction(emoji_) # adds the reactions to the message

    index = {}
    for cmd in [cmd for cmd in self.bot.commands if not cmd.hidden]: # loops through the commands if the command is not hidden
      category = type(cmd.cog).__name__
      if category not in index:
        index[category] = {}
      index[category][cmd.name] = cmd.description
    if command and command not in index.keys():
      for cmd in self.bot.commands:
        if cmd.name == command:
            if not cmd.usage:
              return await ctx.send("That command has no usage")
            embed = discord.Embed().set_author(name=f"{cmd.name}", icon_url=ctx.author.avatar_url)
            embed.description=f"{cmd.usage}"
            return await ctx.send(embed=embed)
      return await ctx.send("There's no help for that command")

    default = discord.Embed(color=0x00ff77) # create a discord embed
    default.set_author(name="Help Menu", icon_url=self.bot.user.avatar_url) # set some info to the embed
    value = "\n".join(
      [
        f"• `{category}` - {len(commands_)} commands"
        for category, commands_ in index.items()
      ]
    )
    default.add_field(name="◈ Categories", value=value)

    embeds = [default]
    for category, commands_ in index.items():
      e = discord.Embed(color=0x00ff77)
      e.set_author(name=category, icon_url=self.bot.user.avatar_url)
      e.set_thumbnail(url=ctx.guild.icon_url)
      e.description = "\n".join(
        [f"\n• `{cmd}` - {desc}" for cmd, desc in commands_.items()]
      )
      embeds.append(e)

    pos = 0
    if command:
      pos = [c.lower() for c in index.keys()].index(command.lower()) + 1
    try:
      await ctx.message.delete()
    except discord.errors.Forbidden:
      pass
    msg = await ctx.send(embed=embeds[pos])
    emojis = ["⏮", "◀️", "⏹", "▶️", "⏭"]
    self.bot.loop.create_task(add_reactions(msg))
    while True:

      def predicate(react, usr):
        return (
          react.message.id == msg.id
          and usr == ctx.author
          and str(react.emoji) in emojis
        )

      try:
        reaction, user = await self.bot.wait_for(
          "reaction_add", timeout=60.0, check=predicate
        )
      except asyncio.TimeoutError:
        return await msg.clear_reactions()

      emoji = str(reaction.emoji)
      try:
        await msg.remove_reaction(reaction, user)
      except discord.errors.Forbidden:
        await ctx.send("unfortunately bot is missing some permissions so you have to remove your reaction yourself", delete_after=1.2)
      i = emojis.index(emoji)
      if pos > 0 and i < 2:
        if i == 0:
          pos = 0
        else:
          pos -= 1
      elif pos < len(embeds) - 1 and i > 2:
        if i == 3:
          pos += 1
        else:
          pos = len(embeds) - 1
      elif i == 2:
        return await msg.delete()
      else:
        continue

      embeds[pos].set_footer(text=f"Page {pos + 1}/{len(embeds)}")
      await msg.edit(embed=embeds[pos])


def setup(bot):
  bot.add_cog(Core(bot))