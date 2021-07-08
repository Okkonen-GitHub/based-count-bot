import os
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.ext.commands import Context
from discord.ext.commands import check
from discord.errors import NotFound
import discord
import json

import sqlite3


def is_dev(ctx):
  with open(f"{os.path.dirname(__file__)}/config.json", "r") as f:
    conf = json.load(f)
  return str(ctx.author.id) in conf["devs"].values()

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
    sql = "SELECT * from users ORDER BY based_count"
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

  @check(is_dev)
  @command(name="ct", hidden=True)
  async def _ct(self, ctx):
    self.db.cursor.execute(
      '''
      CREATE TABLE IF NOT EXISTS "users" (
      "user_id"	TEXT NOT NULL UNIQUE,
      "based_count"	INTEGER DEFAULT 0
      )
      '''
    )

  @check(is_dev)
  @command(name='emtpytable', aliases = ["cleardb", "cleartable"])
  async def _emtpydb(self, ctx, *, q:str):
    if q == "yes i am very sure":
      self.db.cursor.execute(
        '''
        DROP TABLE "users"
        '''
      )
    else:
      await ctx.send("Are you sure tho? Use `cleartable yes i am very sure")

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
                await message.channel.send(content=f"{message.mentions[0]} has now based count of {int(query[0])+1}", delete_after=5)
              if not query:
                self.db.insert(message.mentions[0].id, 1)
                await message.channel.send(content=f"{message.mentions[0]} has now based count of 1, their first one!", delete_after=5)


  @command(name='leaderboard', aliases = ['lb', 'leaderb', 'top'], usage="`b!leaderboard`", description="Show the top 10 most based users")
  async def _leaderboard(self, ctx):
    """Show the leaderboard sorted and 'paged' """
    
    result = self.db.select_all()


    leader_board = {}    

    for i, user in enumerate(reversed(range(len(result)))):
      try:
        username = await self.bot.fetch_user(result[user][0])
      except NotFound:
        username = "User not found"
      leader_board[i] = username, result[user][1]
    
    top_ten = {}
    for i, user in enumerate(range(len(leader_board))):
      if i < 10:
        top_ten[i] = leader_board[user]
        leader_board.pop(i)
      else:
        break

    default = discord.Embed(color=0xdd6666)
    default.set_author(name="Leaderboard", icon_url=self.bot.user.avatar_url)
    value = "\n".join(
      [
        f"`{pos+1}.` -  {usr[0]} - Score: {usr[1]}"
        for pos, usr, in top_ten.items()
      ]
    )
    default.add_field(name="Top 10", value=value)

    await ctx.send(embed=default)
  
  @command(name='stats', aliases = ["stat"], usage="`b!stats [@user]`", description="Show your or someone elses stats")
  async def _stats(self, ctx: Context, user: discord.User = None):
    try:
      e = discord.Embed(color=0xdd6666).set_author(name="Stats", icon_url=self.bot.user.avatar_url)
      if user is None:
        result = self.db.get_based(ctx.author.id)
        e.add_field(name="Your based score is: ", value=f"{result[0]}")
      elif user is not None:
        result = self.db.get_based(user.id)
        e.add_field(name=f"{user.name} has a based score of: ", value=f"{result[0]}")
      await ctx.send(embed=e)
    
    except TypeError as err:
      await ctx.send(f"User not found in database [{err}]")
  

def setup(bot):
  bot.add_cog(Counter(bot))
  