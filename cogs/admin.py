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
import checks, boss_utils

class adminCog(commands.Cog): 
	def __init__(self, bot):
		self.bot = bot

		self.boss_info_db = self.bot.db.boss
		self.guild_info_db = self.bot.db.guild
		self.command_info_db = self.bot.db.command

	async def cog_before_invoke(self, ctx : commands.Context):
		await self.bot.wait_until_ready()

	################ !입장 ################ 		
	@commands.has_permissions(manage_guild=True)
	@commands.command(name = "!입장")
	async def text_channel_setting(self, ctx: commands.Context):
		curr_text_channel = ctx.message.channel

		if curr_text_channel.id == int(self.bot.guild_setting_info[str(ctx.guild.id)]["textchannel"]):
			return await ctx.send(f"현재 설정된 `명령어채널`과 동일합니다.")

		set_text_channel_name : str = ctx.guild.get_channel(int(self.bot.guild_setting_info[str(ctx.guild.id)]["textchannel"]))
		if set_text_channel_name is None:
			self.bot.guild_setting_info = (str(ctx.guild.id), "textchannel", curr_text_channel.id, 0)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"textchannel" : curr_text_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : 명령어채널 [{curr_text_channel.name}] 설정완료!")
			return await ctx.send(f"`명령어채널`이 **[{curr_text_channel.name}]** 채널로 설정되었습니다.\n`음성채널` 접속 후 `!소환` 명령을 통해 `음성채널`을 설정해 주세요.")
		
		emoji_list : list = ["⭕", "❌"]
		channel_error_message = await ctx.send(f"현재 **[{set_text_channel_name}]** 채널이 `명령어채널`로 설정되어 있습니다.\n해당 채널로 `명령어채널`을 변경 하시려면 ⭕ 그대로 사용하시려면 ❌ 를 눌러주세요.\n(10초이내 미입력시 기존 채널 그대로 설정됩니다.)", tts=False)

		for emoji in emoji_list:
			await channel_error_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == channel_error_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)
		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			return await ctx.send(f"시간이 초과됐습니다. **[{set_text_channel_name}]** 채널에서 사용해주세요!")

		if str(reaction) == "⭕":
			self.bot.guild_setting_info = (str(ctx.guild.id), "textchannel", curr_text_channel.id, 0)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"textchannel" : curr_text_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : 명령어채널 [{curr_text_channel.name}] 설정완료!")
			return await ctx.send(f"`명령어채널`이 **[{curr_text_channel.name}]** 채널로 설정되었습니다.")
		else:
			return await ctx.send(f"`명령어채널` 설정이 취소되었습니다.\n**[{set_text_channel_name}]** 채널에서 사용해주세요!")

	################ !소환 ################ 		
	@commands.has_permissions(manage_guild=True)
	@commands.command(name = "!소환")
	async def voice_channel_setting(self, ctx: commands.Context):
		if not await boss_utils.setting_check(ctx, self.bot):
			return

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
				self.bot.voice_client_list = (str(ctx.guild.id), await curr_voice_channel.connect(reconnect=True))

			self.bot.guild_setting_info = (str(ctx.guild.id), "voicechannel", curr_voice_channel.id, 0)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"voicechannel" : curr_voice_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : 음성채널 [{curr_voice_channel.name}] 설정완료!")
			return await ctx.send(f"`음성채널`이 **[{curr_voice_channel.name}]** 채널로 설정되었습니다.\n`!게임설정` [게임명:`린엠`, `린2엠`] 명령을 통해 게임 정보를 설정해 주세요.")
		
		emoji_list : list = ["⭕", "❌"]
		channel_error_message = await ctx.send(f"현재 **[{set_voice_channel_name}]** 채널이 `음성채널`로 설정되어 있습니다.\n해당 채널로 `음성채널`을 변경 하시려면 ⭕ 그대로 사용하시려면 ❌ 를 눌러주세요.\n(10초이내 미입력시 기존 채널 그대로 설정됩니다.)", tts=False)

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
				self.bot.voice_client_list = (str(ctx.guild.id), await curr_voice_channel.connect(reconnect=True))
			
			self.bot.guild_setting_info = (str(ctx.guild.id), "voicechannel", curr_voice_channel.id, 0)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"voicechannel" : curr_voice_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : 음성채널 [{curr_voice_channel.name}] 설정완료!")
			return await ctx.send(f"`음성채널`이 **[{curr_voice_channel.name}]** 채널로 설정되었습니다.")
		else:
			return await ctx.send(f"`음성채널` 설정이 취소되었습니다.\n**[{set_voice_channel_name}]** 채널에서 사용해주세요!")

	################ !게임설정 ################ 		
	@commands.has_permissions(manage_guild=True)
	@commands.command(name = "!게임설정")
	async def game_setting(self, ctx: commands.Context, *, game_name : str = None):
		if not await boss_utils.setting_check(ctx, self.bot):
			return

		if not game_name:
			return await ctx.send(f"`게임이름`을 입력해주세요.(`린엠`, `린2엠`)")

		curr_game_name : str = self.bot.guild_setting_info[str(ctx.guild.id)]["game_name"]

		if curr_game_name == game_name:
			return await ctx.send(f"현재 설정된 게임[`{curr_game_name}`]과 동일합니다.")
		
		if game_name not in ["린엠", "린2엠"]:
			return await ctx.send(f"올바른 `게임이름`을 입력해주세요.(`린엠`, `린2엠`)")

		if self.guild_info_db.guilds_boss.find_one({"_id" : str(ctx.message.guild.id)}):
			emoji_list : list = ["⭕", "❌"]
			game_delete_message = await ctx.send(f"현재 [`{curr_game_name}`] 정보로 설정되어 있습니다.\n해당 게임 정보를 삭제하고 `{game_name}` 정보로 변경하시려면 ⭕ 그대로 사용하시려면 ❌ 를 눌러주세요.\n(10초이내 미입력시 기존 게임 그대로 설정됩니다.)", tts=False)

			for emoji in emoji_list:
				await game_delete_message.add_reaction(emoji)

			def reaction_check(reaction, user):
				return (reaction.message.id == game_delete_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)
			try:
				reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
			except asyncio.TimeoutError:
				return await ctx.send(f"시간이 초과됐습니다. [`{curr_game_name}`] 설정을 사용합니다.")

			if str(reaction) == "⭕":
				self.guild_info_db.guilds_boss.delete_one({"_id" : str(ctx.message.guild.id)})
			else:
				return await ctx.send(f"[`{game_name}`] 설정이 취소되었습니다!\n[`{curr_game_name}`] 설정을 사용합니다.")

		await ctx.send(f"`{game_name}` 정보를 설정합니다.\n게임 설정에 다소 `시간`이 걸립니다.\n`완료 메세지`가 나올 때까지 기다려주시기 바랍니다.")

		boss_data : list = []
		fixed_boss_data : list = []
		result_boss_data : dict = {"_id":str(ctx.guild.id)}
		result_fixed_boss_data : dict = {"_id":str(ctx.guild.id)}

		if game_name == "린엠":
			boss_data = boss_utils.set_boss_data(list(self.boss_info_db.lin_m_boss.find({})), "boss", self.bot.timezone)
			fixed_boss_data = boss_utils.set_boss_data(list(self.boss_info_db.lin_m_fixed_boss.find({})), "fixed_boss", self.bot.timezone)
		else:
			boss_data = boss_utils.set_boss_data(list(self.boss_info_db.lin_2m_boss.find({})), "boss", self.bot.timezone)
			fixed_boss_data = boss_utils.set_boss_data(list(self.boss_info_db.lin_2m_fixed_boss.find({})), "fixed_boss", self.bot.timezone)

		for data in boss_data:
			result_boss_data.update(data)

		for data in fixed_boss_data:
			result_fixed_boss_data.update(data)

		self.bot.guild_setting_info = (str(ctx.guild.id), "game_name", game_name, 0)
		self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {"game_name" : game_name}}, upsert=True)
		self.guild_info_db.guilds_boss.delete_one({"_id":str(ctx.guild.id)})
		self.guild_info_db.guilds_boss.insert_one(result_boss_data)
		self.guild_info_db.guilds_fixed_boss.delete_one({"_id":str(ctx.guild.id)})
		self.guild_info_db.guilds_fixed_boss.insert_one(result_fixed_boss_data)

		print(f"{ctx.message.guild.name} 서버 : 게임 [{game_name}] 설정완료!")
		return await ctx.send(f"게임 [`{game_name}`] 설정완료!\n`!설정완료` 명령을 통해 설정을 완료해 주세요")

	################ !설정완료 ################ 		
	@commands.has_permissions(manage_guild=True)
	@commands.command(name = "!설정완료")
	async def game_setting_finish(self, ctx: commands.Context):
		if not await boss_utils.setting_check(ctx, self.bot):
			return

		if self.bot.guild_setting_info[str(ctx.guild.id)]["setting_finish"]:
			return await ctx.send(f"이미 게임 설정이 완료돼 있습니다.")

		self.bot.guild_setting_info = (str(ctx.guild.id), "setting_finish", True, 0)
		self.guild_info_db.guilds.update_one({"_id" : str(ctx.message.guild.id)}, {"$set" : {"setting_finish" : True}}, upsert=True)

		print(f"{ctx.message.guild.name} 서버 : 보탐봇 설정완료!")
		return await ctx.send(f"`보탐봇` 설정완료!\n `보탐봇` 스타트!")

	################ !채널설정 ################ 		
	@commands.has_permissions(manage_guild=True)
	@commands.command(name = "!채널설정")
	async def etc_channel_setting(self, ctx: commands.Context, *, args : str = None):
		if not await boss_utils.setting_check(ctx, self.bot):
			return

		if not args:
			return await ctx.send(f"채널 설정을 원하는 `명령어`를 입력바랍니다.(`게임`, `척살`, `아이템`)")
		
		if args == "게임":
			key = "gamechannel"
		elif args == "척살":
			key = "killchannel"
		elif args == "아이템":
			key = "itemchannel"
		else:
			return await ctx.send(f"올바른 `명령어`를 입력바랍니다.(`게임`, `척살`, `아이템`)")

		curr_channel = ctx.message.channel

		if curr_channel.id == int(self.bot.guild_setting_info[str(ctx.guild.id)][key]):
			return await ctx.send(f"현재 설정된 `{args}채널`과 동일합니다.")

		set_channel_name : str = ctx.guild.get_channel(int(self.bot.guild_setting_info[str(ctx.guild.id)][key]))
		if set_channel_name is None:
			self.bot.guild_setting_info = (str(ctx.guild.id), key, curr_channel.id, 0)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {key : curr_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : {args}채널 [{curr_channel.name}] 설정완료!")
			return await ctx.send(f"`{args}채널`이 **[{curr_channel.name}]** 채널로 설정되었습니다.")
		
		emoji_list : list = ["⭕", "❌"]
		channel_error_message = await ctx.send(f"현재 **[{set_channel_name}]** 채널이 `{args}채널`로 설정되어 있습니다.\n해당 채널로 `{args}채널`을 변경 하시려면 ⭕ 그대로 사용하시려면 ❌ 를 눌러주세요.\n(10초이내 미입력시 기존 채널 그대로 설정됩니다.)", tts=False)

		for emoji in emoji_list:
			await channel_error_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == channel_error_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)
		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			return await ctx.send(f"시간이 초과됐습니다. **[{set_channel_name}]** 채널에서 사용해주세요!")

		if str(reaction) == "⭕":
			self.bot.guild_setting_info = (str(ctx.guild.id), key, curr_channel.id, 0)
			self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {key : curr_channel.id}}, upsert=True)
			print(f"{ctx.author.guild.name} 서버 : {args}채널 [{curr_channel.name}] 설정완료!")
			return await ctx.send(f"`{args}채널`이 **[{curr_channel.name}]** 채널로 설정되었습니다.")
		else:
			return await ctx.send(f"`{args}채널` 설정이 취소되었습니다.\n**[{set_channel_name}]** 채널에서 사용해주세요!")

	################ !기타설정 ################ 		
	@commands.has_permissions(manage_guild=True)
	@commands.command(name = "!기타설정")
	async def etc_value_setting(self, ctx: commands.Context, *, args : str = None):
		if not await boss_utils.setting_check(ctx, self.bot):
			return

		input_value : list = args.split()

		if len(input_value) != 2:
			return await ctx.send(f"변경을 원하는 `설정` 및 `값`을 입력바랍니다.(설정 : `알림1`, `알림2`, `자동멍`, `멍삭제`)")
		
		try:
				input_value[1] = int(input_value[1])
		except ValueError:
			return await ctx.send(f"`값`은 숫자로 입력바랍니다.")

		tmp_str : str = "분"

		if input_value[0] == "알림1":
			key = "before_alert"
		elif input_value[0] == "알림2":
			key = "before_alert1"
		elif input_value[0] == "자동멍":
			key = "mungChk"
		elif input_value[0] == "멍삭제":
			key = "delmungcnt"
			tmp_str = "회"
		else:
			return await ctx.send(f"올바른 `명령어`를 입력바랍니다.(`알림1`, `알림2`, `자동멍`, `멍삭제`)")

		if input_value[1] == int(self.bot.guild_setting_info[str(ctx.guild.id)][key]):
			return await ctx.send(f"현재 설정된 `{input_value[0]}`값(`{int(self.bot.guild_setting_info[str(ctx.guild.id)][key])}{tmp_str}`)이 입력된 값(`{input_value[1]}{tmp_str}`)과 동일합니다.")

		set_value : str = input_value[1]

		self.bot.guild_setting_info = (str(ctx.guild.id), key, set_value, 0)
		self.guild_info_db.guilds.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {key : set_value}}, upsert=True)
		print(f"{ctx.author.guild.name} 서버 : {input_value[0]}값 [{input_value[1]}{tmp_str}] 설정완료!")
		return await ctx.send(f"`{input_value[0]}`값이 **[{input_value[1]}{tmp_str}]**(으)로 설정되었습니다.")

	################ !명령변경 ################ 		
	@commands.has_permissions(manage_guild=True)
	@commands.command(name = "!명령변경")
	async def set_custom_command(self, ctx: commands.Context, *, args : str = None):
		if not await boss_utils.setting_check(ctx, self.bot):
			return

		if not args or len(args.split()) != 2:
			return await ctx.send(f"변경을 원하는 [`명령어`] [`변경명령어`]를 입력바랍니다.")

		custom_command_input : list = args.split()
		
		if self.guild_info_db.commands.find_one({"_id" : str(ctx.guild.id)}) is None:
			if self.bot.bosscommandSetting.get(custom_command_input[0]) is None:
				return await ctx.send(f"올바른 [`명령어`]를 입력바랍니다.")
			result_custom_command = custom_command_input[0]
		else:
			tmp_dict : dict = self.guild_info_db.commands.find_one({"_id" : str(ctx.guild.id)})
			if custom_command_input[0] not in tmp_dict.values() and custom_command_input[0] not in tmp_dict.keys():
				if self.bot.bosscommandSetting.get(custom_command_input[0]) is None:
					return await ctx.send(f"올바른 [`명령어`]를 입력바랍니다.")
				result_custom_command = custom_command_input[0]
			elif custom_command_input[0] in tmp_dict.keys():
				result_custom_command = custom_command_input[0]
			elif custom_command_input[0] in tmp_dict.values():
				result_dict : dict = { v : k for k, v in tmp_dict.items()}
				result_custom_command = result_dict.get(custom_command_input[0])
			else:
				return await ctx.send(f"올바른 [`명령어`]를 입력바랍니다.")

		self.bot.guild_custom_command_info = (str(ctx.guild.id), result_custom_command, custom_command_input[1], 0)
		self.guild_info_db.commands.update_one({"_id" : str(ctx.guild.id)}, {"$set" : {result_custom_command : custom_command_input[1]}}, upsert=True)
		
		return await ctx.send(f"[`{custom_command_input[0]}`]가 [`{custom_command_input[1]}`](으)로 변경되었습니다.")

def setup(bot):
  bot.add_cog(adminCog(bot))
