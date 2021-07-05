import os
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands import guild_only
import discord

import sqlite3


class DataBase:
  
  db_path = f"{os.path.dirname(os.path.abspath(__file__))}/based.sqlite"

  def __init__(self):
    self.db = sqlite3.connect(self.db_path)
    self.cursor = self.db.cursor()

  
  def commit(self):
    self.db.commit()

  def execute(self, sql, values):
      self.cursor.execute(sql, values)


  def update(self, value, UserId):
    try:
      sql = "UPDATE users SET user_id = ?, based_count = ?  WHERE user_id = ?"
      val = (UserId, value, UserId)
      self.execute(sql, val)
      self.commit()
    except sqlite3.Error as err:
      return f"Something went wrong: [{err}]"
    finally:
      return f"Updated db"

  def select_all(self):
    sql = "SELECT * from users"
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    return result

  def get_based(self, UserId):
    sql = "SELECT based_count FROM users WHERE user_id = ?"
    self.execute(sql, (UserId,))
    based_count = self.cursor.fetchone()
    return based_count
  
  def insert(self, userID, initialCount):
    sql = "INSERT INTO users(user_id, based_count) VALUES(?, ?)"
    val = (userID, (str(initialCount)))
    self.execute(sql, val)
    self.commit()
    return "Inserted to db"



class Counter(Cog):

  db = DataBase()

  def __init__(self, bot):
    self.bot = bot

  @Cog.listener()
  async def on_message(self, message: discord.Message):
    if not message.author.bot:
      if message.content is not None:
        if len(message.mentions) > 0:
          if not message.author in message.mentions and "based" in message.content:
            if "based" in message.content:
              query = self.db.get_based(message.mentions[0].id)
              if query:
                self.db.update(int(query[0]) + 1, message.mentions[0].id)
                await message.channel.send(content=f"{message.mentions[0]} has now based count of {int(query[0])+1}")
              if not query:
                self.db.insert(message.mentions[0].id, 1)
                await message.channel.send(content=f"{message.mentions[0]} has now based count of 1")


  @command(name='leaderboard', aliases = ['lb', 'leaderb', ''])
  async def _leaderboard(self, ctx,):
    result = self.db.select_all()
    e = discord.Embed(color=0xdd6666)
    e.add_field(name="Leaderboard", value=f"{result}")
    await ctx.send(embed=e)
  

def setup(bot):
  bot.add_cog(Counter(bot))
  