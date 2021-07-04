import random
from discord.ext.commands import command
from discord.ext.commands import Cog
import discord


class Stats(Cog):

  def __init__(self, bot):
    self.bot = bot

  @command(description="flips a coin", aliases = ["flip", "cflip", "coin"])
  async def coinflip(self, ctx):
    coin = ["heads", "tails"]
    flipped = (random.choice(coin))
    return await ctx.send(f"The coin landed on {flipped}")

def setup(bot):
  bot.add_cog(Stats(bot))