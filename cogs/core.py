
import discord
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands import check
from discord.ext.commands import ExtensionError


# from main import CogList
# from main import starttime

import json
import os


def is_dev(ctx):
  with open(f"{os.path.dirname(__file__)}", "r") as f:
    conf = json.load(f)
  return str(ctx.author.id) in conf["devs"].values()

class Core(Cog):

  def __init__(self, bot) -> None:
    self.bot = bot
  
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
    
    except ExtensionError as err:
      await ctx.send(f"Failed to unoad {ext} [{err}]")
      print(f"Failed to unoad {ext} [{err}]")
  
  @command(name='list_ext', aliases = ["extls", "ls", "lsext", "loaded", "list"])
  async def _list_ext(self, ctx,):
    e = discord.Embed(color = 0xff5100) # create a discord embed
    cog_list = list(self.bot.cogs) # make loaded cogs into a list
    e.set_author(name = "These are the loaded cogs at the moment") # set the embed author
    for cog in cog_list: # loop through the cog list
        e.add_field( # add loaded cog to embed
            name = "Loaded Cog:",
            value = f"{cog}",
            inline=False
    )
    await ctx.send(embed = e)

  @command(name='reload', aliases = ["rext", "extr", "re"])
  async def _reload(self, ctx, ext = "all"):
    active_cogs = list(self.bot.cogs)
    e = discord.Embed(color=0xff5100)
    if ext == "all":
      for cog in active_cogs:
        try:
          if not cog == "Core":
            self.bot.reload_extension(cog)
            e.add_field(name=f"Reloaded succesfully:", value=f"{cog}")
        except ExtensionError as err:
          e.add_field(name=f"failed to reload [{err}]", value=f"{cog}")
    else:
      try:
        self.bot.reload_extension(f"cogs.{ext}")
        e.add_field(name=f"Reloaded succesfully:", value=f"{ext}")
      except ExtensionError as err:
        e.add_field(name=f"failed to reload [{err}]", value=f"{ext}")
    await ctx.send(embed = e)

def setup(bot):
  bot.add_cog(Core(bot))