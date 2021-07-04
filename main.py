import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=".")


@bot.event
async def on_ready():
  return print(f"Logged in as {bot.user}\nAvailable in servers: {bot.guilds}")
  # TODO start status changer


@bot.event
async def on_message(message):
  print(message)

# TODO add cogs


def main(secret):
  bot.run(secret)


if __name__ == "__main__":
  with open(f'{os.path.dirname(__file__)}/secrets.txt') as secrets:
    secret = secrets.readline()
  main(secret)