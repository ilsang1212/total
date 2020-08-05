import asyncio
import discord
import datetime
import logging
from discord.ext import tasks, commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument
import aiohttp
from pymongo import MongoClient
import pymongo, ssl, traceback, random
from github import Github
import base64
import discordbot_total
import checks, boss_utils

class adminCog(commands.Cog): 
	bot_setting = discordbot_total.ilsang_total_bot

	def __init__(self, bot):
		self.bot = bot

		self.guild_info_db = self.bot.db.boss.guilds

	# @commands.command(name = "프리픽스", aliases = ["ㅍㄹ"])
	# async def prefix_add_(self, ctx: commands.Context, *, prefix : str):
	# 	"""프리픽스 변경, 최대 10개 등록 가능"""
	# 	if not prefix:
	# 		return await ctx.send(f"변경할 prefix를 입력하세요.")

	# 	prefix_list = prefix.split()

	# 	await self.bot.set_guild_prefixes(ctx.guild, prefix_list)
	# 	self.guild_info_db.update_one({"_id" : str(ctx.message.guild.id)}, {"$set" : {"guild_prefix":prefix_list}}, upsert=True)
	# 	await ctx.send(f"prefix **[{prefix}]**로 변경완료!")

def setup(bot):
  bot.add_cog(adminCog(bot))


