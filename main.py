import asyncio
import json
import os
import random
import discord
from discord.ext.commands import Bot
from discord.ext.commands import when_mentioned_or
from discord.ext.commands import ExtensionError
from datetime import datetime

class CogList:

  cogs = [
    "cogs.core",
  ]


bot = Bot(command_prefix=when_mentioned_or("b!"))
bot.remove_command("help")

bot_uptime = None

@bot.event
async def on_ready():
  global bot_uptime
  print(f"Logged in as {bot.user}\nAvailable in servers: {bot.guilds[0]}")
  bot_uptime = datetime.now() # save the timedelta when bot is activated
  bot.loop.create_task(status_changer())
  await load_all_cogs()


@bot.event
async def on_message(message: discord.Message):
  if not message.content:
    return
  if message.mentions:
    print(message.mentions + "is based")
    pass 



async def load_all_cogs():
  for cog in CogList.cogs:
    try:
      bot.load_extension(cog)
      print(f"loaded ext {cog}")
    except ExtensionError as err:
      print(f"Failed to load ext {cog}: [{err}]")
  return print("\nloaded cogs")


async def status_changer():
  with open(f'{os.path.dirname(__file__)}/config.json') as conf:
    config = json.load(conf)
  while True:
    await asyncio.sleep(20)
    activity = random.choice(config["activities"])
    await bot.change_presence(activity=discord.Activity(name=activity["name"], type=discord.ActivityType[activity["status"]]))

def main(secret):
  bot.run(secret)


if __name__ == "__main__":
  with open(f'{os.path.dirname(__file__)}/secrets.txt') as secrets:
    secret = secrets.readline()
  main(secret)