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

class settingCog(commands.Cog): 
	bot_setting = discordbot_total.ilsang_total_bot

	def __init__(self, bot):
		self.bot = bot

	################ 채널등록 ################ 
	@commands.command(name="!리로드", aliases=["ㄹ"])
	async def command_reload_cog(self, ctx : commands.Context, *, cog_file_names : str = None):
		reload_cog_file_list : list = self.bot.cog_list.copy() if not cog_file_names else cog_file_names.split()
		respond_text : str = f"총 {len(reload_cog_file_list)}개의 리로드 결과:\n"

		for cog_file_name in reload_cog_file_list:
			try:
				try:
					self.bot.reload_extension(f"cogs.{cog_file_name}")
				except:
					self.bot.load_extension(f"cogs.{cog_file_name}")
				respond_text += f"`{cog_file_name}` 로드 완료!\n"
				if cog_file_name not in self.bot.cog_list:
					self.bot.cog_list.append(cog_file_name)
			except:
				traceback_result : list = traceback.format_exc().split("\n")
				respond_text += f"**`{cog_file_name}` 로드 실패!**\n```py\n{traceback_result}\n```"

		await ctx.send(respond_text[:1999])

	################ 채널등록 ################ 
	@commands.command(name="!길드업데이트", aliases=["ㄱㄷ"])
	async def command_guild_update(self, ctx : commands.Context, *, cog_file_names : str = None):
		guild_info, text_channel_name, text_channel_id, voice_channel_name, voice_channel_id = utils.get_guild_channel_info(self.bot)
		guild_db_info : list = []
		init_guild_db : dict = {}

		for guild in guild_info:
			guild_document : dict = self.bot.db.boss.guilds.find_one({"_id": str(guild.id)})
			if not guild_document:
				init_guild_db = {
					"_id" : str(guild.id),
					"guild_name" : str(guild.name),
					"voicechannel" : 0,
					"textchannel" : 0,
					"gamechannel" : 0,
					"killchannel" : 0,
					"itemchannel" : 0,
					"before_alert" : "1",
					"before_alert1" : "5",
					"mungChk" : "10",
					"delmungcnt" : "5",
					"bossInfoNum" : "3",
					"restarttime" : "04:30",
					"restartPeriod" : "1",
					"game_name" : "",
					}
				self.bot.db.boss.guilds.insert_one(init_guild_db)

		print(f"접속 길드 수 : {len(guild_info)}")
		await ctx.send(f"길드 업데이트 완료!")
		await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"길드 업데이트 완료!", type=1), afk = False)

	################ 채널등록 ################ 
	@commands.command(name="!보스업데이트", aliases=["보스업"])
	async def command_guild_update(self, ctx : commands.Context, *, cog_file_names : str = None):
		lin_m_boss_result : dict = utils.get_boss_data("lin_m_boss.ini", self.bot.repo)
		print(lin_m_boss_result)
		await ctx.send(f"보스 업데이트 완료!")


def setup(bot):
  bot.add_cog(settingCog(bot))


