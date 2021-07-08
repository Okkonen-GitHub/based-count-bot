import random
from discord.ext.commands import command
from discord.ext.commands import Cog


class Misc(Cog):

  def __init__(self, bot):
    self.bot = bot

  @command(description="flips a coin", aliases = ["flip", "cflip", "coin"], hidden=True)
  async def coinflip(self, ctx):
    coin = ["heads", "tails"]
    flipped = (random.choice(coin))
    return await ctx.send(f"The coin landed on {flipped}")
  
  @command(name='based', aliases = [], hidden=True)
  async def _based(self, ctx):
    await ctx.send("I'm already based enough")

def setup(bot):
  bot.add_cog(Misc(bot))