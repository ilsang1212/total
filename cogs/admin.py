from discord.ext import tasks, commands
import traceback
import datetime
import discord
import discordbot_jungsan
import checks

class adminCog(commands.Cog): 
	commandSetting : list = discordbot_jungsan.ilsang_distribution_bot.commandSetting

	def __init__(self, bot):
		self.bot = bot
		
		self.member_db = self.bot.db.jungsan.member
		self.jungsan_db = self.bot.db.jungsan.jungsandata
		self.guild_db = self.bot.db.jungsan.guild
		self.backup_db = self.bot.db.backup.backupdata

		self.backup_data.start()

	################ 현재시간 확인 ################ 
	@commands.command(name="!현재시간", aliases=["!ㅎㅈㅅㄱ"])
	async def current_time_check(self, ctx):
		embed = discord.Embed(
			title = f"현재시간은 {datetime.datetime.now().strftime('%H')}시 {datetime.datetime.now().strftime('%M')}분 {datetime.datetime.now().strftime('%S')}초 입니다.",
			color=0xff00ff
			)
		return await ctx.send(embed = embed, tts=False)

	################ 상태메세지 변경 ################ 
	@commands.command(name="!상태", aliases=["!ㅅㅌ"])
	async def status_modify(self, ctx, *, args : str = None):
		await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name=args, type=1), afk = False)
		return await ctx.send(f"< 상태메세지 [{args}]로 변경완료 >", tts=False)

	################ 백업 Task ################ 
	@tasks.loop(hours=24.0)
	async def backup_data(self):
		# "_id" : int = 순번
		# "regist" : int = 등록자ID
		# "getdate" : datetime = 등록날짜
		# "boss" : str = 보스명
		# "item" : str = 아이템명
		# "toggle" : str = 루팅자
		# "itemstatus" : str = 아이템상태(미판매, 분배중, 분배완료)
		# "price" : int = 가격
		# "each_price" : int = 분배가격
		# "before_jungsan_ID" : list = 참석명단(분배전)
		# "after_jungsan_ID" : list = 참석명단(분배후)
		# "modifydate" : datetime = 수정날짜

		backup_date = datetime.datetime.now() - datetime.timedelta(days = int(self.bot.basicSetting[4]))

		jungsan_document :list = []
		backup_jungsan_document : list = []

		jungsan_document = list(self.jungsan_db.find({"itemstatus":"분배중"}))

		for jungsan_data in jungsan_document:
			if jungsan_data['modifydate'] < backup_date:
				self.jungsan_db.delete_one({"_id":jungsan_data['_id']})
				del jungsan_data['_id']
				backup_jungsan_document.append(jungsan_data)

		self.backup_db.insert_many(backup_jungsan_document)

	################ Cogs 리로드 ################ 
	@commands.has_permissions(manage_guild=True)
	@commands.command(name="!리로드", aliases=["!ㄹㄹㄷ"])
	async def command_reload_cog(self, ctx : commands.Context, *, cog_lists : str = None):
		reload_cog_list : list = self.bot.cog_list.copy() if not cog_lists else cog_lists.split()
		respond_text : str = f"총 {len(reload_cog_list)}개의 리로드 결과:\n"
		respond_text1 : str = f"총 {len(reload_cog_list)}개의 리로드 결과:\n"

		for extension in reload_cog_list:
			try:
				try:
					self.bot.reload_extension(f"{extension}")
				except:
					self.bot.load_extension(f"{extension}")
				respond_text += f"`{extension}` 로드 완료!\n"
				if extension not in self.bot.cog_list:
					self.bot.cog_list.append(extension)
				respond_text1 += f"`{extension}` 로드 완료!\n"
			except:
				traceback_result : list = traceback.format_exc()#.split("\n")
				respond_text += f"**`{extension}` 로드 실패!**\n"
				respond_text1 += f"**`{extension}` 로드 실패!**\n{traceback_result}"

		print(respond_text1)

		return await ctx.send(respond_text, tts=False)

	################ member_db초기화 ################ .
	@checks.is_manager()
	@commands.has_permissions(manage_guild=True)
	@commands.command(name=commandSetting[0][0], aliases=commandSetting[0][1:])
	async def initialize_all_member_data(self, ctx):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		emoji_list : list = ["⭕", "❌"]

		delete_warning_message = await ctx.send(f"**혈원데이터를 초기화 하시면 다시는 복구할 수 없습니다. 정말로 초기화하시겠습니까?**\n**초기화 : ⭕ 취소: ❌**\n(20초 동안 입력이 없을시 초기화가 취소됩니다.)", tts=False)
		
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 20)
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
	@commands.command(name=commandSetting[1][0], aliases=commandSetting[1][1:])
	async def initialize_all_jungsan_data(self, ctx):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		emoji_list : list = ["⭕", "❌"]

		delete_warning_message = await ctx.send(f"**정산데이터를 초기화 하시면 다시는 복구할 수 없습니다. 정말로 초기화하시겠습니까?**\n**초기화 : ⭕ 취소: ❌**\n(20초 동안 입력이 없을시 초기화가 취소됩니다.)", tts=False)
		
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 20)
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
	@commands.command(name=commandSetting[2][0], aliases=commandSetting[2][1:])
	async def initialize_all_guild_data(self, ctx):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		emoji_list : list = ["⭕", "❌"]

		delete_warning_message = await ctx.send(f"**혈비데이터를 초기화 하시면 다시는 복구할 수 없습니다. 정말로 초기화하시겠습니까?**\n**초기화 : ⭕ 취소: ❌**\n(20초 동안 입력이 없을시 초기화가 취소됩니다.)", tts=False)
		
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 20)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **초기화**를 취소합니다!")

		if str(reaction) == "⭕":
			self.guild_db.delete_many({})
			print(f"< 혈비데이터 초기화 완료 >")
			return await ctx.send(f"☠️ 혈비데이터 초기화 완료! ☠️")
		else:
			return await ctx.send(f"**초기화**가 취소되었습니다.\n")	

	################ backup_db초기화 ################
	@checks.is_manager()
	@commands.has_permissions(manage_guild=True)
	@commands.command(name=commandSetting[3][0], aliases=commandSetting[3][1:])
	async def initialize_all_backup_data(self, ctx):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		emoji_list : list = ["⭕", "❌"]

		delete_warning_message = await ctx.send(f"**백업데이터를 초기화 하시면 다시는 복구할 수 없습니다. 정말로 초기화하시겠습니까?**\n**초기화 : ⭕ 취소: ❌**\n(20초 동안 입력이 없을시 초기화가 취소됩니다.)", tts=False)
		
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 20)
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
		
def setup(bot):
  bot.add_cog(adminCog(bot))


