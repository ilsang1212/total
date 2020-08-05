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
	bot_setting = discordbot_jungsan.ilsang_distribution_bot

	def __init__(self, bot):
		self.bot = bot
		
		self.member_db = self.bot.db.jungsan.member
		self.jungsan_db = self.bot.db.jungsan.jungsandata
		self.guild_db = self.bot.db.jungsan.guild
		self.guild_db_log = self.bot.db.jungsan.guild_log
		self.backup_db = self.bot.db.backup.backupdata
		
	################ 기본설정확인 ################ 
	@commands.command(name=bot_setting.jungsancommandSetting[46][0], aliases=bot_setting.jungsancommandSetting[46][1:])
	async def setting_info(self, ctx):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return

		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		embed = discord.Embed(
			title = f"⚙️ 기본 설정(v5)",
			color=0xff00ff
			)
		embed.add_field(name = f"🚫 삭제 주기", value = f"```{self.bot.basicSetting[4]} 일```")
		embed.add_field(name = f"⌛ 체크 시간", value = f"```{self.bot.basicSetting[5]} 초```")
		embed.add_field(name = f"⚖️ 수수료", value = f"```{self.bot.basicSetting[7]} %```")
		embed.add_field(name = f"🗨️ 명령 채널", value = f"```{ctx.message.channel.name}```")
		return await ctx.send(embed = embed, tts=False)

	################ 현재시간 확인 ################ 
	@commands.command(name=bot_setting.jungsancommandSetting[37][0], aliases=bot_setting.jungsancommandSetting[37][1:])
	async def current_time_check(self, ctx):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return

		embed = discord.Embed(
			title = f"현재시간은 {datetime.datetime.now().strftime('%H')}시 {datetime.datetime.now().strftime('%M')}분 {datetime.datetime.now().strftime('%S')}초 입니다.",
			color=0xff00ff
			)
		return await ctx.send(embed = embed, tts=False)

	################ 상태메세지 변경 ################ 
	@commands.command(name=bot_setting.jungsancommandSetting[38][0], aliases=bot_setting.jungsancommandSetting[38][1:])
	async def status_modify(self, ctx, *, args : str = None):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return

		if not args:
			return await ctx.send(f"**{self.bot.commandSetting[38][0]} [내용]** 양식으로 변경 해주세요")

		await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name=args, type=1), afk = False)
		return await ctx.send(f"< 상태메세지 **[ {args} ]**로 변경완료 >", tts=False)

	################ member_db초기화 ################ .
	@checks.is_manager()
	@commands.has_permissions(manage_guild=True)
	@commands.command(name=bot_setting.jungsancommandSetting[0][0], aliases=bot_setting.jungsancommandSetting[0][1:])
	async def initialize_all_member_data(self, ctx):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return

		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		emoji_list : list = ["⭕", "❌"]

		delete_warning_message = await ctx.send(f"**혈원데이터를 초기화 하시면 다시는 복구할 수 없습니다. 정말로 초기화하시겠습니까?**\n**초기화 : ⭕ 취소: ❌**\n({int(self.bot.basicSetting[5])*2}초 동안 입력이 없을시 초기화가 취소됩니다.)", tts=False)
		
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = int(self.bot.basicSetting[5])*2)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **초기화**를 취소합니다!")

		if str(reaction) == "⭕":
			self.member_db.delete_many({})
			print(f"< 혈원데이터 초기화 완료 >")
			return await ctx.send(f"☠️ 혈원데이터 초기화 완료! ☠️")
		else:
			return await ctx.send(f"**초기화**가 취소되었습니다.\n")		

	################ jungsan_db초기화 ################
	@checks.is_manager()
	@commands.has_permissions(manage_guild=True)
	@commands.command(name=bot_setting.jungsancommandSetting[1][0], aliases=bot_setting.jungsancommandSetting[1][1:])
	async def initialize_all_jungsan_data(self, ctx):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return

		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		emoji_list : list = ["⭕", "❌"]

		delete_warning_message = await ctx.send(f"**정산데이터를 초기화 하시면 다시는 복구할 수 없습니다. 정말로 초기화하시겠습니까?**\n**초기화 : ⭕ 취소: ❌**\n({int(self.bot.basicSetting[5])*2}초 동안 입력이 없을시 초기화가 취소됩니다.)", tts=False)
		
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = int(self.bot.basicSetting[5])*2)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **초기화**를 취소합니다!")

		if str(reaction) == "⭕":
			self.jungsan_db.delete_many({})
			print(f"< 정산데이터 초기화 완료 >")
			return await ctx.send(f"☠️ 정산데이터 초기화 완료! ☠️")
		else:
			return await ctx.send(f"**초기화**가 취소되었습니다.\n")		

	################ guild_db초기화 ################
	@checks.is_manager()
	@commands.has_permissions(manage_guild=True)
	@commands.command(name=bot_setting.jungsancommandSetting[2][0], aliases=bot_setting.jungsancommandSetting[2][1:])
	async def initialize_all_guild_data(self, ctx):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return
		
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		emoji_list : list = ["⭕", "❌"]

		delete_warning_message = await ctx.send(f"**혈비데이터를 초기화 하시면 다시는 복구할 수 없습니다. 정말로 초기화하시겠습니까?**\n**초기화 : ⭕ 취소: ❌**\n({int(self.bot.basicSetting[5])*2}초 동안 입력이 없을시 초기화가 취소됩니다.)", tts=False)
		
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = int(self.bot.basicSetting[5])*2)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **초기화**를 취소합니다!")

		if str(reaction) == "⭕":
			self.guild_db.delete_many({})
			self.guild_db_log.delete_many({})
			init_guild_data : dict = {
				"guild_money":0,
				"back_up_period":14,
				"checktime":15,
				"distributionchannel":0,
				"tax":5
				}
			update_guild_data : dict = self.guild_db.update_one({"_id":"guild"}, {"$set":init_guild_data}, upsert = True)

			self.bot.basicSetting[4] = init_guild_data['back_up_period']
			self.bot.basicSetting[5] = init_guild_data['checktime']
			self.bot.basicSetting[6] = init_guild_data['distributionchannel']
			self.bot.basicSetting[7] = init_guild_data['tax']
			
			# basicSetting[4] = backup_period
			# basicSetting[5] = checktime
			# basicSetting[6] = distributionchannel
			# basicSetting[7] = tax

			print(f"< 혈비/로그 데이터 초기화 완료 >")
			return await ctx.send(f"☠️ 혈비/로그 데이터 초기화 완료! ☠️\n**[{self.bot.commandSetting[36][0]}]** 명령어를 입력하신 후 사용해주시기 바랍니다.")
		else:
			return await ctx.send(f"**초기화**가 취소되었습니다.\n")	

	################ backup_db초기화 ################
	@checks.is_manager()
	@commands.has_permissions(manage_guild=True)
	@commands.command(name=bot_setting.jungsancommandSetting[3][0], aliases=bot_setting.jungsancommandSetting[3][1:])
	async def initialize_all_backup_data(self, ctx):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return

		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		emoji_list : list = ["⭕", "❌"]

		delete_warning_message = await ctx.send(f"**백업데이터를 초기화 하시면 다시는 복구할 수 없습니다. 정말로 초기화하시겠습니까?**\n**초기화 : ⭕ 취소: ❌**\n({int(self.bot.basicSetting[5])*2}초 동안 입력이 없을시 초기화가 취소됩니다.)", tts=False)
		
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = int(self.bot.basicSetting[5])*2)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **초기화**를 취소합니다!")

		if str(reaction) == "⭕":
			self.backup_db.delete_many({})
			print(f"< 백업데이터 초기화 완료 >")
			return await ctx.send(f"☠️ 백업데이터 초기화 완료! ☠️")
		else:
			return await ctx.send(f"**초기화**가 취소되었습니다.\n")

	################ 혈비로그확인 ################ 
	@checks.is_manager()
	@commands.command(name=bot_setting.jungsancommandSetting[47][0], aliases=bot_setting.jungsancommandSetting[47][1:])
	async def guild_log_load(self, ctx, *, args : str = None):
		if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
			return

		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if args:
			return await ctx.send(f"**{self.bot.commandSetting[47][0]}** 양식으로 등록 해주세요")

		result : list = []

		result = list(self.guild_db_log.find({}))

		if len(result) == 0:
			return await ctx.send(f"```혈비 로그가 없습니다!```")

		sorted_result = sorted(list([result_data['log_date'] for result_data in result]))

		log_date_list : list = []
		log_date_list = sorted(list(set([result_data['log_date'].strftime('%y-%m-%d') for result_data in result])))
		
		total_distribute_money : int = 0
		embed_list : list = []
		embed_limit_checker : int = 0
		embed_cnt : int = 0
		detail_title_info	: str = ""
		detail_info	: str = ""
		
		embed = discord.Embed(
					title = f"📜 혈비 로그",
					description = "",
					color=0x00ff00
					)
		embed_list.append(embed)
		for date in log_date_list:
			embed_limit_checker = 0
			detail_info	: str = ""
			for result_data1 in result:
				if embed_limit_checker == 50:
					embed_limit_checker = 0
					embed_cnt += 1
					tmp_embed = discord.Embed(
						title = "",
						description = "",
						color=0x00ff00
						)
					embed_list.append(tmp_embed)
				if result_data1['log_date'].strftime('%y-%m-%d') == date:
					embed_limit_checker += 1
					if result_data1['in_out_check']:
						if result_data1['reason'] != "":
							detail_info += f"+ 💰 {result_data1['money']} : {', '.join(result_data1['member_list'])} (사유:{result_data1['reason']})\n"
						else:
							detail_info += f"+ 💰 {result_data1['money']} : 혈비 입금\n"
					else:
						if result_data1['reason'] != "":
							detail_info += f"- 💰 {result_data1['money']} : {', '.join(result_data1['member_list'])} (사유:{result_data1['reason']})\n"
						else:
							detail_info += f"- 💰 {result_data1['money']} : {', '.join(result_data1['member_list'])}\n"
				
				embed_list[embed_cnt].title = f"🗓️ {date}"
				embed_list[embed_cnt].description = f"```diff\n{detail_info}```"

			if len(embed_list) > 1:
				for embed_data in embed_list:
					await asyncio.sleep(0.1)
					await ctx.send(embed = embed_data)
			else:
				await asyncio.sleep(0.1)
				await ctx.send(embed = embed)
		return
		
def setup(bot):
  bot.add_cog(adminCog(bot))


