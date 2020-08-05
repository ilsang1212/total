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

class settingCog(commands.Cog): 
	bot_setting = discordbot_total.ilsang_total_bot

	def __init__(self, bot):
		self.bot = bot

	################ 채널등록 ################ 
	@commands.command(name="리로드", aliases=["ㄹ"])
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

	# ################ 채널등록 ################ 
	# @commands.has_permissions(manage_guild=True)
	# @commands.command(name=bot_setting.jungsancommandSetting[36][0], aliases=bot_setting.jungsancommandSetting[36][1:])
	# async def join_channel(self, ctx, *, args : str = None):
	# 	if self.bot.basicSetting[6] == "" or self.bot.basicSetting[6] == 0:
	# 		channel = ctx.message.channel.id #메세지가 들어온 채널 ID

	# 		print (f"[ {self.bot.basicSetting[6]} ]")
	# 		print (f"] {ctx.message.channel.name} [")

	# 		self.bot.basicSetting[6] = str(channel)
	# 		print(self.bot.basicSetting[6])

	# 		result = self.guild_db.update_one({"_id":"guild"}, {"$set":{"distributionchannel":str(channel)}}, upsert = True)
	# 		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
	# 			return await ctx.send(f"{ctx.author.mention}, 정산 내역 삭제 주기 설정 실패.")   

	# 		await ctx.send(f"< 텍스트채널 [{ctx.message.channel.name}] 접속완료 >", tts=False)
			
	# 		print(f"< 텍스트채널 [ {self.bot.get_channel(int(self.bot.basicSetting[6])).name} ] 접속완료>")
	# 	else:
	# 		for guild in self.bot.guilds:
	# 			for text_channel in guild.text_channels:
	# 				if self.bot.basicSetting[6] == str(text_channel.id):
	# 					curr_guild_info = guild
	# 					print(curr_guild_info.name, guild.name, curr_guild_info.get_channel(int(self.bot.basicSetting[6])).name)

	# 		emoji_list : list = ["⭕", "❌"]
	# 		guild_error_message = await ctx.send(f"이미 **[{curr_guild_info.name}]** 서버 **[{curr_guild_info.get_channel(int(self.bot.basicSetting[6])).name}]** 채널이 명령어 채널로 설정되어 있습니다.\n해당 채널로 명령어 채널을 변경 하시려면 ⭕ 그대로 사용하시려면 ❌ 를 눌러주세요.\n({self.bot.basicSetting[5]}이내 미입력시 기존 설정 그대로 설정됩니다.)", tts=False)

	# 		for emoji in emoji_list:
	# 			await guild_error_message.add_reaction(emoji)

	# 		def reaction_check(reaction, user):
	# 			return (reaction.message.id == guild_error_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)
	# 		try:
	# 			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = int(self.bot.basicSetting[5]))
	# 		except asyncio.TimeoutError:
	# 			return await ctx.send(f"시간이 초과됐습니다. **[{curr_guild_info.name}]** 서버 **[{curr_guild_info.get_channel(self.bot.basicSetting[6]).name}]** 채널에서 사용해주세요!")
			
	# 		if str(reaction) == "⭕":
	# 			self.bot.basicSetting[6] = str(ctx.message.channel.id)

	# 			print ('[ ', self.bot.basicSetting[6], ' ]')
	# 			print ('] ', ctx.message.channel.name, ' [')
			
	# 			result = self.guild_db.update_one({"_id":"guild"}, {"$set":{"distributionchannel":str(self.bot.basicSetting[6])}}, upsert = True)
	# 			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
	# 				return await ctx.send(f"{ctx.author.mention}, 정산 내역 삭제 주기 설정 실패.")

	# 			return await ctx.send(f"명령어 채널이 **[{ctx.author.guild.name}]** 서버 **[{ctx.message.channel.name}]** 채널로 새로 설정되었습니다.")
	# 		else:
	# 			return await ctx.send(f"명령어 채널 설정이 취소되었습니다.\n**[{curr_guild_info.name}]** 서버 **[{curr_guild_info.get_channel(int(self.bot.basicSetting[6])).name}]** 채널에서 사용해주세요!")

	# ################ 백업주기 설정 ################ 
	# @checks.is_manager()
	# @commands.command(name=bot_setting.jungsancommandSetting[40][0], aliases=bot_setting.jungsancommandSetting[40][1:])
	# async def set_backup_time(self, ctx, *, args : str = None):
	# 	if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
	# 		return

	# 	member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

	# 	if not member_data:
	# 		return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

	# 	if not args:
	# 		return await ctx.send(f"**{self.bot.commandSetting[40][0]} [숫자]** 양식으로 등록 해주세요")
		
	# 	try:
	# 		args = int(args)
	# 	except ValueError:
	# 		return await ctx.send(f"**정산 내역 삭제 주기는 [숫자]** 로 입력 해주세요")

	# 	self.bot.basicSetting[4] = args
	# 	result = self.guild_db.update_one({"_id":"guild"}, {"$set":{"back_up_period":args}}, upsert = True)
	# 	if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
	# 		return await ctx.send(f"{ctx.author.mention}, 정산 내역 삭제 주기 설정 실패.")   

	# 	return  await ctx.send(f"정산 내역 삭제 주기를 **[{args}]**일로 설정 하였습니다.")

	# ################ 확인시간 설정 ################ 
	# @checks.is_manager()
	# @commands.command(name=bot_setting.jungsancommandSetting[41][0], aliases=bot_setting.jungsancommandSetting[41][1:])
	# async def set_check_time(self, ctx, *, args : str = None):
	# 	if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
	# 		return

	# 	member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

	# 	if not member_data:
	# 		return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

	# 	if not args:
	# 		return await ctx.send(f"**{self.bot.commandSetting[41][0]} [숫자]** 양식으로 등록 해주세요")
		
	# 	try:
	# 		args = int(args)
	# 	except ValueError:
	# 		return await ctx.send(f"**이모지 확인 시간은 [숫자]** 로 입력 해주세요")

	# 	self.bot.basicSetting[5] = args
	# 	print(self.bot.basicSetting[5])

	# 	result = self.guild_db.update_one({"_id":"guild"}, {"$set":{"checktime":args}}, upsert = True)
	# 	if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
	# 		return await ctx.send(f"{ctx.author.mention}, 이모지 확인 시간 설정 실패.")   

	# 	return  await ctx.send(f"이모지 확인 시간을 **[{args}]**초로 설정 하였습니다.")

	# ################ 세금 설정 ################ 
	# @checks.is_manager()
	# @commands.command(name=bot_setting.jungsancommandSetting[42][0], aliases=bot_setting.jungsancommandSetting[42][1:])
	# async def set_tax(self, ctx, *, args : str = None):
	# 	if ctx.message.channel.id != int(self.bot.basicSetting[6]) or self.bot.basicSetting[6] == "":
	# 		return

	# 	member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

	# 	if not member_data:
	# 		return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

	# 	if not args:
	# 		return await ctx.send(f"**{self.bot.commandSetting[42][0]} [숫자]** 양식으로 등록 해주세요")
		
	# 	try:
	# 		args = int(args)
	# 	except ValueError:
	# 		return await ctx.send(f"**세율은 시간은 [숫자]** 로 입력 해주세요")

	# 	self.bot.basicSetting[7] = args
	# 	print(self.bot.basicSetting[7])

	# 	result = self.guild_db.update_one({"_id":"guild"}, {"$set":{"tax":args}}, upsert = True)
	# 	if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
	# 		return await ctx.send(f"{ctx.author.mention}, 세율 설정 실패.")   

	# 	return  await ctx.send(f"세율을 **[{args}]**%로 설정 하였습니다.")

def setup(bot):
  bot.add_cog(settingCog(bot))


