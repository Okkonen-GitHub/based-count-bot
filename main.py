import asyncio
import json
import os
import random
import discord
from discord.ext.commands import Bot
from discord.ext.commands import when_mentioned_or
from discord.ext.commands import ExtensionError
import datetime

class CogList:

  cogs = [
    "cogs.core",
    "cogs.counter",
    "cogs.misc",
  ]


bot = Bot(command_prefix=when_mentioned_or("b!"))
bot.remove_command("help")

bot_uptime = datetime.datetime.now() 

@bot.event
async def on_ready():
  global bot_uptime
  print(f"Logged in as {bot.user}\nAvailable in servers: {bot.guilds[0]}")
  bot.loop.create_task(status_changer())
  await load_all_cogs()




async def load_all_cogs():
  for cog in CogList.cogs:
    try:
      bot.load_extension(cog)
      print(f"loaded ext {cog}")
    except ExtensionError as err:
      print(f"Failed to load ext {cog}: [{err}]")
  return print("\nloaded cogs")


async def status_changer():
  with open(f'{os.path.dirname(__file__)}/cogs/config.json') as conf:
    config = json.load(conf)
  while True:
    await asyncio.sleep(20)
    activity = random.choice(config["activities"])
    await bot.change_presence(activity=discord.Activity(name=activity["name"], type=discord.ActivityType[activity["status"]]))


def starttime(current_time):
    """takes the current time and returns the bot's uptime"""
    uptime = current_time - bot_uptime
    return uptime


def main(secret):
  bot.run(secret)


if __name__ == "__main__":
  with open(f'{os.path.dirname(__file__)}/secrets.txt') as secrets:
    secret = secrets.readline()
  main(secret)