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
import checks, utils

class adminCog(commands.Cog): 
	bot_setting = discordbot_total.ilsang_total_bot

	def __init__(self, bot):
		self.bot = bot

	################ 현재시간 확인 ################ 
	@commands.command(name=bot_setting._bosscommandSetting[37][0], aliases=bot_setting._bosscommandSetting[37][1:])
	async def current_time_check(self, ctx):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return

		embed = discord.Embed(
			title = f"현재시간은 {datetime.datetime.now().strftime('%H')}시 {datetime.datetime.now().strftime('%M')}분 {datetime.datetime.now().strftime('%S')}초 입니다.",
			color=0xff00ff
			)
		return await ctx.send(embed = embed, tts=False)

def setup(bot):
  bot.add_cog(adminCog(bot))


