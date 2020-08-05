from discord.ext import commands
from pymongo import MongoClient
import discord

def is_manager():
  async def pred(ctx : commands.Context) -> bool:
    user_info : dict = ctx.bot.db.jungsan.member.find_one({"_id":ctx.author.id})
    if not user_info:
      return False

    if "manager" in user_info["permissions"]:
      return True
      
    return False
  return commands.check(pred)