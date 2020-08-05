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
import discordbot_total, test
import checks, boss_utils

class adminCog(commands.Cog): 
	bot_setting = discordbot_total.ilsang_total_bot

	def __init__(self, bot):
		self.bot = bot

		self.boss_info_db = self.bot.db.boss
		self.guild_info_db = self.bot.db.guild

	@commands.has_permissions(manage_messages=True)
	@commands.command(name = "!입장")
	async def text_channel_setting(self, ctx: commands.Context):
		curr_text_channel = ctx.message.channel

		if curr_text_channel.id == int(self.bot.guild_setting_info[str(ctx.guild.id)]["textchannel"]):
			return await ctx.send(f"현재 설정된 `명령어채널`과 동일합니다.")

		set_text_channel_name : str = ctx.guild.get_channel(int(self.bot.guild_setting_info[str(ctx.guild.id)]["textchannel"]))
		if set_text_channel_name is None:
			self.bot.guild_setting_info = (str(ctx.guild.id), "textchannel", curr_text_channel.id)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"textchannel" : curr_text_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : 명령어채널 [{curr_text_channel.name}] 설정완료!")
			return await ctx.send(f"`명령어채널`이 **[{curr_text_channel.name}]** 채널로 설정되었습니다.")
		
		emoji_list : list = ["⭕", "❌"]
		channel_error_message = await ctx.send(f"이미 **[{set_text_channel_name}]** 채널이 `명령어채널`로 설정되어 있습니다.\n해당 채널로 `명령어채널`을 변경 하시려면 ⭕ 그대로 사용하시려면 ❌ 를 눌러주세요.\n(10초이내 미입력시 기존 채널 그대로 설정됩니다.)", tts=False)

		for emoji in emoji_list:
			await channel_error_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == channel_error_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)
		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			return await ctx.send(f"시간이 초과됐습니다. **[{set_text_channel_name}]** 채널에서 사용해주세요!")

		if str(reaction) == "⭕":
			self.bot.guild_setting_info = (str(ctx.guild.id), "textchannel", curr_text_channel.id)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"textchannel" : curr_text_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : 명령어채널 [{curr_text_channel.name}] 설정완료!")
			return await ctx.send(f"`명령어채널`이 **[{curr_text_channel.name}]** 채널로 새로 설정되었습니다.")
		else:
			return await ctx.send(f"`명령어채널` 설정이 취소되었습니다.\n**[{set_text_channel_name}]** 채널에서 사용해주세요!")

	@commands.has_permissions(manage_messages=True)
	@commands.command(name = "!소환")
	async def voice_channel_setting(self, ctx: commands.Context):
		if not ctx.author.voice:
			return await ctx.send(f":no_entry_sign: 현재 접속중인 `음성채널`이 없습니다.\n`음성채널`에 먼저 들어가주세요.")

		curr_voice_channel = ctx.author.voice.channel

		if curr_voice_channel.id == int(self.bot.guild_setting_info[str(ctx.guild.id)]["voicechannel"]):
			return await ctx.send(f"현재 설정된 `음성채널`과 동일합니다.")

		set_voice_channel_name : str = ctx.guild.get_channel(int(self.bot.guild_setting_info[str(ctx.guild.id)]["voicechannel"]))
		if set_voice_channel_name is None:
			if ctx.voice_client is not None:
				if ctx.voice_client.is_playing():
					ctx.voice_client.stop()

				await ctx.voice_client.move_to(curr_voice_channel)
			else:
				self.bot.voice_client_list = (ctx.guild.id, await curr_voice_channel.connect(reconnect=True))

			self.bot.guild_setting_info = (str(ctx.guild.id), "voicechannel", curr_voice_channel.id)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"voicechannel" : curr_voice_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : 음성채널 [{curr_voice_channel.name}] 설정완료!")
			return await ctx.send(f"`음성채널`이 **[{curr_voice_channel.name}]** 채널로 설정되었습니다.")
		
		emoji_list : list = ["⭕", "❌"]
		channel_error_message = await ctx.send(f"이미 **[{set_voice_channel_name}]** 채널이 `음성채널`로 설정되어 있습니다.\n해당 채널로 `음성채널`을 변경 하시려면 ⭕ 그대로 사용하시려면 ❌ 를 눌러주세요.\n(10초이내 미입력시 기존 채널 그대로 설정됩니다.)", tts=False)

		for emoji in emoji_list:
			await channel_error_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == channel_error_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)
		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			return await ctx.send(f"시간이 초과됐습니다. **[{set_voice_channel_name}]** 채널에서 사용해주세요!")

		if str(reaction) == "⭕":
			if ctx.voice_client is not None:
				if ctx.voice_client.is_playing():
					ctx.voice_client.stop()

				await ctx.voice_client.move_to(curr_voice_channel)
			else:
				self.bot.voice_client_list = (ctx.guild.id, await curr_voice_channel.connect(reconnect=True))
			
			self.bot.guild_setting_info = (str(ctx.guild.id), "voicechannel", curr_voice_channel.id)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"voicechannel" : curr_voice_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : 음성채널 [{curr_voice_channel.name}] 설정완료!")
			return await ctx.send(f"`음성채널`이 **[{curr_voice_channel.name}]** 채널로 새로 설정되었습니다.")
		else:
			return await ctx.send(f"`음성채널` 설정이 취소되었습니다.\n**[{set_voice_channel_name}]** 채널에서 사용해주세요!")

	@commands.command(name = "!게임설정")
	async def game_setting(self, ctx: commands.Context, *, game_name : str):
		if not game_name:
			return await ctx.send(f"`게임이름`을 입력해주세요(`린엠`, `린2엠`).")
		
		if game_name not in ["린엠", "린2엠"]:
			return await ctx.send(f"올바른 `게임이름`을 입력해주세요(`린엠`, `린2엠`).")

		boss_data : list = []
		fixed_boss_data : list = []

		if game_name == "린엠":
			boss_data = boss_utils.set_boss_data(list(self.boss_info_db.lin_m_boss.find({})), "boss", self.bot.timezone)
			fixed_boss_data = boss_utils.set_boss_data(list(self.boss_info_db.lin_m_fixed_boss.find({})), "fixed_boss", self.bot.timezone)
		else:
			boss_data = boss_utils.set_boss_data(list(self.boss_info_db.lin_2m_boss.find({})), "boss", self.bot.timezone)
			fixed_boss_data = boss_utils.set_boss_data(list(self.boss_info_db.lin_2m_fixed_boss.find({})), "fixed_boss", self.bot.timezone)

		self.guild_info_db.guilds.update_one({"_id" : str(ctx.message.guild.id)}, {"$set" : {"game_name" : game_name, "setting_finish" : True}}, upsert=True)
		for data in boss_data:
			self.guild_info_db.guilds_boss.update_one({"_id" : str(ctx.message.guild.id)}, {"$set" : data}, upsert=True)
		for data in fixed_boss_data:
			self.guild_info_db.guilds_fixed_boss.update_one({"_id" : str(ctx.message.guild.id)}, {"$set" : data}, upsert=True)

		print(f"{ctx.message.guild.name} 서버 : 게임 [{game_name}] 설정완료!")
		return await ctx.send(f"게임 [`{game_name}`] 설정완료!")

	@commands.command(name = "변경")
	async def test_setting(self, ctx: commands.Context, *, args : str):
		self.bot.test_text = args
		return 

def setup(bot):
  bot.add_cog(adminCog(bot))


