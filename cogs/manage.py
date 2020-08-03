from discord.ext import commands
import discord
import datetime
import asyncio
import checks
import discordbot_jungsan

class manageCog(commands.Cog): 
	commandSetting : list = discordbot_jungsan.ilsang_distribution_bot.commandSetting

	def __init__(self, bot):
		self.bot = bot
		self.index_value = 0
				
		self.member_db = self.bot.db.jungsan.member
		self.jungsan_db = self.bot.db.jungsan.jungsandata
		self.guild_db = self.bot.db.jungsan.guild

		try:
			self.db_index = self.jungsan_db.find().sort([("_id",-1)]).limit(1)
			self.index_value = list(self.db_index)[0]["_id"]
		except:
			pass

	################ 참여자 ################ 
	################ 참여내역 및 정산금 확인 ################ 
	@commands.command(name="!정산확인")
	async def participant_data_check(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		jungsan_document : list = []
		if not args:
			jungsan_document = list(self.jungsan_db.find({"$and" : [{"before_jungsan_ID" : member_data['game_ID']}, {"$or" : [{"itemstatus" : "분배중"}, {"itemstatus" : "미판매"}]}]}))
		else:
			input_distribute_all_finish : list = args.split()
			len_input_distribute_all_finish = len(input_distribute_all_finish)

			if len_input_distribute_all_finish != 2:
				return await ctx.send(f"**명령어 [검색조건] [검색값]** 형식으로 입력 해주세요! **[검색조건]**은 **[순번, 보스명, 아이템, 날짜, 분배상태]** 다섯가지 중 **1개**를 입력 하셔야합니다!")
			else:
				if input_distribute_all_finish[0] == "순번":
					try:
						input_distribute_all_finish[1] = int(input_distribute_all_finish[1])
					except:
						return await ctx.send(f"**[순번] [검색값]**은 \"숫자\"로 입력 해주세요!")
					jungsan_document = list(self.jungsan_db.find({"$and" : [{"before_jungsan_ID" : member_data['game_ID']}, {"_id":input_distribute_all_finish[1]}, {"$or" : [{"itemstatus" : "분배중"}, {"itemstatus" : "미판매"}]}]}))
				elif input_distribute_all_finish[0] == "보스명":
					jungsan_document = list(self.jungsan_db.find({"$and" : [{"before_jungsan_ID" : member_data['game_ID']}, {"boss":input_distribute_all_finish[1]}, {"$or" : [{"itemstatus" : "분배중"}, {"itemstatus" : "미판매"}]}]}))
				elif input_distribute_all_finish[0] == "아이템":
					jungsan_document = list(self.jungsan_db.find({"$and" : [{"before_jungsan_ID" : member_data['game_ID']}, {"item":input_distribute_all_finish[1]}, {"$or" : [{"itemstatus" : "분배중"}, {"itemstatus" : "미판매"}]}]}))
				elif input_distribute_all_finish[0] == "날짜":
					try:
						start_search_date : str = datetime.datetime.now().replace(year = int(input_distribute_all_finish[1][:4]), month = int(input_distribute_all_finish[1][5:7]), day = int(input_distribute_all_finish[1][8:10]), hour = 0, minute = 0, second = 0)
						end_search_date : str = start_search_date + datetime.timedelta(days = 1)
					except:
						return await ctx.send(f"**[날짜] [검색값]**은 0000-00-00 형식으로 입력 해주세요!")
					jungsan_document = list(self.jungsan_db.find({"$and" : [{"before_jungsan_ID" : member_data['game_ID']}, {"getdate":{"$gte":start_search_date, "$lt":end_search_date}}, {"$or" : [{"itemstatus" : "분배중"}, {"itemstatus" : "미판매"}]}]}))
				elif input_distribute_all_finish[0] == "분배상태":
					if input_distribute_all_finish[1] == "분배중":
						jungsan_document = list(self.jungsan_db.find({"$and" : [{"before_jungsan_ID" : member_data['game_ID']}, {"itemstatus" : "분배중"}]}))
					elif input_distribute_all_finish[1] == "미판매":
						jungsan_document = list(self.jungsan_db.find({"$and" : [{"before_jungsan_ID" : member_data['game_ID']}, {"itemstatus" : "미판매"}]}))
					else:
						return await ctx.send(f"**[분배상태] [검색값]**은 \"미판매\" 혹은 \"분배중\"로 입력 해주세요!")
				else:
					return await ctx.send(f"**[검색조건]**이 잘못 됐습니다. **[검색조건]**은 **[순번, 보스명, 아이템, 날짜, 분배상태]** 다섯가지 중 **1개**를 입력 하셔야합니다!")

		if len(jungsan_document) == 0:
			return await ctx.send(f"{ctx.author.mention}님! 수령할 정산 내역이 없습니다.")

		total_money : int = 0
		toggle_list : list = []
		toggle_list = sorted(list(set([jungsan_data['toggle'] for jungsan_data in jungsan_document])))

		embed = discord.Embed(
				title = f"===== [{member_data['game_ID']}]님 정산 내역 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = f"🏦 **[ 은행 ]**", value = f"**```fix\n {member_data['account']}```**")
		for game_id in toggle_list:
			each_price : int = 0
			info_cnt : int = 0
			tmp_info : list = []
			tmp_info.append("")
			for jungsan_data in jungsan_document:
				if jungsan_data['toggle'] == game_id:
					if jungsan_data['itemstatus'] == "미판매":
						if len(tmp_info[info_cnt]) > 900:
							tmp_info.append("")
							info_cnt += 1
						tmp_info[info_cnt] += f"-[순번:{jungsan_data['_id']}]|{jungsan_data['getdate'].strftime('%Y-%m-%d')}|{jungsan_data['boss']}|{jungsan_data['item']}|{jungsan_data['itemstatus']}\n"
					else:
						each_price += jungsan_data['each_price']
						tmp_info[info_cnt] += f"+[순번:{jungsan_data['_id']}]|{jungsan_data['getdate'].strftime('%Y-%m-%d')}|{jungsan_data['boss']}|{jungsan_data['item']}|💰{jungsan_data['each_price']}\n"
			total_money += each_price
			if len(tmp_info) > 1:
				embed.add_field(
					name = f"[ {game_id} ]님께 받을 내역 (총 💰 {each_price} )",
					value = f"```diff\n{tmp_info[0]}```",
					inline = False
					)
				for i in range(len(tmp_info)-1):
					embed.add_field(
						name = f"\u200b",
						value = f"```diff\n{tmp_info[i+1]}```",
						inline = False
						)
			else:
				embed.add_field(
						name = f"[ {game_id} ]님께 받을 내역 (총 💰 {each_price} )",
						value = f"```diff\n{tmp_info[0]}```",
						inline = False
						)
		await ctx.send(embed = embed)
		if int(total_money) == 0:
			return
		else:
			
			embed1 = discord.Embed(
				title = f"총 수령 예정 금액 : 💰 {total_money}",
				description = "",
				color=0x00ff00
				)
			return await ctx.send(embed = embed1)

	################ 등록자 ################ 
	################ 분배등록 ################ 
	@commands.command(name="!등록")
	async def regist_data(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [보스명] [아이템명] [루팅자] [참여자1] [참여자2]...** 양식으로 등록 해주세요")
		
		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data < 4:
			return await ctx.send(f"**명령어 [보스명] [아이템명] [루팅자] [참여자1] [참여자2]...** 양식으로 등록 해주세요")

		check_member_data : dict = {}
		check_member_list : list = []
		wrong_input_id : list = []
		gulid_money_insert_check : bool = False
		loot_member_data : dict = {}

		if input_regist_data[2] == "혈비":
			gulid_money_insert_check = True
			loot_member_data = {"_id":ctx.author.id}
		else:
			gulid_money_insert_check = False
			loot_member_data = self.member_db.find_one({"game_ID":input_regist_data[2]})
			if not loot_member_data:
				return await ctx.send(f"```루팅자 [{input_regist_data[2]}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")

		check_member_data = list(self.member_db.find())
		for game_id in check_member_data:
			check_member_list.append(game_id['game_ID'])

		for game_id in input_regist_data[3:]:
			if game_id not in check_member_list:
				wrong_input_id.append(game_id)

		if len(wrong_input_id) > 0:
			return await ctx.send(f"```참여자 [{', '.join(wrong_input_id)}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")
		
		input_time : datetime = datetime.datetime.now()
		insert_data : dict = {}
		insert_data = {"regist":str(ctx.author.id),
					"getdate":input_time,
					"boss":input_regist_data[0],
					"item":input_regist_data[1],
					"toggle":input_regist_data[2],
					"toggle_ID":str(loot_member_data["_id"]),
					"itemstatus":"미판매",
					"price":0,
					"each_price":0,
					"before_jungsan_ID":list(set(input_regist_data[3:])),
					"after_jungsan_ID":[],
					"modifydate":input_time,
					"gulid_money_insert":gulid_money_insert_check,
					"bank_money_insert":False
					}
		
		# "_id" : int = 순번
		# "regist" : str = 등록자ID
		# "getdate" : datetime = 등록날짜
		# "boss" : str = 보스명
		# "item" : str = 아이템명
		# "toggle" : str = 루팅자
		# "toggle_ID" : str = 루팅자ID
		# "itemstatus" : str = 아이템상태(미판매, 분배중, 분배완료)
		# "price" : int = 가격
		# "each_price" : int = 분배가격
		# "before_jungsan_ID" : list = 참석명단(분배전)
		# "after_jungsan_ID" : list = 참석명단(분배후)
		# "modifydate" : datetime = 수정날짜
		# "gulid_money_insert" : bool = 혈비등록여부
		# "bank_money_insert" : bool = 은행입금여부

		embed = discord.Embed(
				title = "===== 등록 정보 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = "[ 일시 ]", value = f"```{insert_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		embed.add_field(name = "[ 보스 ]", value = f"```{insert_data['boss']}```")
		embed.add_field(name = "[ 아이템 ]", value = f"```{insert_data['item']}```")
		embed.add_field(name = "[ 루팅 ]", value = f"```{insert_data['toggle']}```")
		embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(insert_data['before_jungsan_ID'])}```")
		await ctx.send(embed = embed)

		data_regist_warning_message = await ctx.send(f"**입력하신 등록 내역을 확인해 보세요!**\n**등록 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 등록이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]

		for emoji in emoji_list:
			await data_regist_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == data_regist_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **등록**를 취소합니다!")

		if str(reaction) == "⭕":
			self.index_value += 1
			result = self.jungsan_db.update_one({"_id":self.index_value}, {"$set":insert_data}, upsert = True)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 등록 실패.") 

			return await ctx.send(f"📥 **[ 순번 : {self.index_value} ]** 정산 등록 완료! 📥")
		else:
			return await ctx.send(f"**등록**이 취소되었습니다.\n")

	################ 등록내역확인 ################ 
	@commands.command(name="!등록확인")
	async def distribute_check(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		visual_flag : int = 0

		jungsan_document : list = []
		if not args:
			jungsan_document : list = list(self.jungsan_db.find({"regist":str(ctx.author.id)}))
		else:
			input_distribute_all_finish : list = args.split()
			
			if input_distribute_all_finish[0] == "상세":
				visual_flag = 1
				del(input_distribute_all_finish[0])
			
			len_input_distribute_all_finish = len(input_distribute_all_finish)

			if len_input_distribute_all_finish == 0:
				jungsan_document : list = list(self.jungsan_db.find({"regist":str(ctx.author.id)}))
			elif len_input_distribute_all_finish != 2:
				return await ctx.send(f"**명령어 (상세) [검색조건] [검색값]** 형식으로 입력 해주세요! **[검색조건]**은 **[순번, 보스명, 아이템, 날짜, 분배상태]** 다섯가지 중 **1개**를 입력 하셔야합니다!")
			else:
				if input_distribute_all_finish[0] == "순번":
					try:
						input_distribute_all_finish[1] = int(input_distribute_all_finish[1])
					except:
						return await ctx.send(f"**[순번] [검색값]**은 \"숫자\"로 입력 해주세요!")
					jungsan_document : list = list(self.jungsan_db.find({"regist":str(ctx.author.id), "_id":input_distribute_all_finish[1]}))
				elif input_distribute_all_finish[0] == "보스명":
					jungsan_document : list = list(self.jungsan_db.find({"regist":str(ctx.author.id), "boss":input_distribute_all_finish[1]}))
				elif input_distribute_all_finish[0] == "아이템":
					jungsan_document : list = list(self.jungsan_db.find({"regist":str(ctx.author.id), "item":input_distribute_all_finish[1]}))
				elif input_distribute_all_finish[0] == "날짜":
					try:
						start_search_date : str = datetime.datetime.now().replace(year = int(input_distribute_all_finish[1][:4]), month = int(input_distribute_all_finish[1][5:7]), day = int(input_distribute_all_finish[1][8:10]), hour = 0, minute = 0, second = 0)
						end_search_date : str = start_search_date + datetime.timedelta(days = 1)
					except:
						return await ctx.send(f"**[날짜] [검색값]**은 0000-00-00 형식으로 입력 해주세요!")
					jungsan_document : list = list(self.jungsan_db.find({"regist":str(ctx.author.id), "getdate":{"$gte":start_search_date, "$lt":end_search_date}}))
				elif input_distribute_all_finish[0] == "분배상태":
					if input_distribute_all_finish[1] == "분배중":
						jungsan_document : list = list(self.jungsan_db.find({"regist":str(ctx.author.id), "itemstatus" : "분배중"}))
					elif input_distribute_all_finish[1] == "미판매":
						jungsan_document : list = list(self.jungsan_db.find({"regist":str(ctx.author.id), "itemstatus" : "미판매"}))
					else:
						return await ctx.send(f"**[분배상태] [검색값]**은 \"미판매\" 혹은 \"분배중\"로 입력 해주세요!")
				else:
					return await ctx.send(f"**[검색조건]**이 잘못 됐습니다. **[검색조건]**은 **[순번, 보스명, 아이템, 날짜, 분배상태]** 다섯가지 중 **1개**를 입력 하셔야합니다!")
		
		if len(jungsan_document) == 0:
			return await ctx.send(f"{ctx.author.mention}님! 등록된 정산 목록이 없습니다.")

		total_distribute_money : int = 0
		embed_list : list = []
		embed_limit_checker : int = 0
		embed_cnt : int = 0
		detail_title_info	: str = ""
		detail_info	: str = ""
		
		embed = discord.Embed(
					title = f"===== [{member_data['game_ID']}]님 등록 내역 =====",
					description = "",
					color=0x00ff00
					)
		embed_list.append(embed)
		for jungsan_data in jungsan_document:
			embed_limit_checker += 1
			if embed_limit_checker == 20:
				embed_limit_checker = 0
				embed_cnt += 1
				tmp_embed = discord.Embed(
					title = "",
					description = "",
					color=0x00ff00
					)
				embed_list.append(tmp_embed)

			if jungsan_data['gulid_money_insert']:
				if jungsan_data['itemstatus'] == "미판매":
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | 혈비적립예정"
					detail_info = f"```fix\n[ 혈비적립 ]```"
				else:
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | 혈비적립완료"
					detail_info = f"~~```fix\n[ 혈비적립 ]```~~"
			elif jungsan_data['bank_money_insert']:
				detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | 은행저축완료"
				detail_info = f"~~```fix\n[ 은행저축 ]```~~"
			else:
				if jungsan_data['itemstatus'] == "분배중":
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | {jungsan_data['itemstatus']} : 1인당 💰{jungsan_data['each_price']}"
					if visual_flag == 0:
						detail_info = f"```fix\n[ 분배중 ] : {len(jungsan_data['before_jungsan_ID'])}명   [ 분배완료 ] : {len(jungsan_data['after_jungsan_ID'])}명```"
					else:
						detail_info = f"```diff\n+ 분 배 중 : {len(jungsan_data['before_jungsan_ID'])}명 (💰{len(jungsan_data['before_jungsan_ID'])*jungsan_data['each_price']})\n{', '.join(jungsan_data['before_jungsan_ID'])}\n- 분배완료 : {len(jungsan_data['after_jungsan_ID'])}명  (💰{len(jungsan_data['after_jungsan_ID'])*jungsan_data['each_price']})\n{', '.join(jungsan_data['after_jungsan_ID'])}```"
					total_distribute_money += len(jungsan_data['before_jungsan_ID'])*int(jungsan_data['each_price'])
				elif jungsan_data['itemstatus'] == "미판매":
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | {jungsan_data['itemstatus']}"
					if visual_flag == 0:
						detail_info = f"```ini\n[ 참여자 ] : {len(jungsan_data['before_jungsan_ID'])}명```"
					else:
						detail_info = f"```ini\n[ 참여자 ] : {len(jungsan_data['before_jungsan_ID'])}명\n{', '.join(jungsan_data['before_jungsan_ID'])}```"
				else:
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | {jungsan_data['itemstatus']} | 💰~~{jungsan_data['price']}~~"
					if visual_flag == 0:
						detail_info = f"~~```yaml\n[ 분배완료 ] : {len(jungsan_data['after_jungsan_ID'])}명```~~"
					else:
						detail_info = f"~~```yaml\n[ 분배완료 ] : {len(jungsan_data['after_jungsan_ID'])}명\n{', '.join(jungsan_data['after_jungsan_ID'])}```~~"

			embed_list[embed_cnt].add_field(name = detail_title_info,
							value = detail_info,
							inline = False)

		if len(embed_list) > 2:
			for embed_data in embed_list:
				await ctx.send(embed = embed_data)
		else:
			await ctx.send(embed = embed)

		embed1 = discord.Embed(
			title = f"총 정산 금액 : 💰 {str(total_distribute_money)}",
			description = "",
			color=0x00ff00
			)
		return await ctx.send(embed = embed1)

	################ 등록내역수정 ################ 
	@commands.command(name="!등록수정")
	async def modify_regist_data(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [보스명] [아이템명] [루팅자] [참여자1] [참여자2]...** 양식으로 등록 해주세요")
		
		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data < 5:
			return await ctx.send(f"**명령어 [순번] [보스명] [아이템명] [루팅자] [참여자1] [참여자2]...** 양식으로 등록 해주세요")
		
		jungsan_data : dict = self.jungsan_db.find_one({"_id":int(input_regist_data[0]), "regist":str(member_data['_id']), "itemstatus":"미판매"})
		
		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 미판매 ]**중이 아니거나 없습니다. **[ !등록확인 ]** 명령을 통해 확인해주세요.\n※등록수정은 **[ 분배상태 ]**가 **[ 미판매 ]** 중인 등록건만 수정 가능합니다!")

		del(input_regist_data[0])

		check_member_data : list = {}
		check_member_list : list = []
		check_member_id_list : list = []
		wrong_input_id : list = []
		gulid_money_insert_check : bool = False
		loot_member_data : dict = {}

		if input_regist_data[2] == "혈비":
			gulid_money_insert_check = True
			loot_member_data["_id"] = ctx.author.id
		else:
			gulid_money_insert_check = False
			loot_member_data = self.member_db.find_one({"game_ID":input_regist_data[2]})
			if not loot_member_data:
				return await ctx.send(f"```루팅자 [{input_regist_data[2]}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")

		check_member_data = list(self.member_db.find())
		for game_id in check_member_data:
			check_member_list.append(game_id['game_ID'])
			if game_id['game_ID'] == input_regist_data[2]:
				loot_member_data["_id"] = game_id['_id']

		for game_id in input_regist_data[3:]:
			if game_id not in check_member_list:
				wrong_input_id.append(game_id)
		
		if len(wrong_input_id) > 0:
			return await ctx.send(f"```참여자 [{', '.join(wrong_input_id)}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")
		
		input_time : datetime = datetime.datetime.now()
		insert_data : dict = {}
		insert_data = {"regist":jungsan_data['regist'],
					"getdate":jungsan_data['getdate'],
					"boss":input_regist_data[0],
					"item":input_regist_data[1],
					"toggle":input_regist_data[2],
					"toggle_ID":str(loot_member_data["_id"]),
					"itemstatus":"미판매",
					"price":0,
					"each_price":0,
					"before_jungsan_ID":list(set(input_regist_data[3:])),
					"after_jungsan_ID":[],
					"modifydate":input_time,
					"gulid_money_insert":gulid_money_insert_check,
					"bank_money_insert":jungsan_data["bank_money_insert"]
					}
		
		embed = discord.Embed(
				title = "===== 수정 정보 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = "[ 순번 ]", value = f"```{self.index_value}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{insert_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		if jungsan_data['boss'] == insert_data['boss']:
			embed.add_field(name = "[ 보스 ]", value = f"```{insert_data['boss']}```")
		else:
			embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']} → {insert_data['boss']}```")
		if jungsan_data['item'] == insert_data['item']:
			embed.add_field(name = "[ 아이템 ]", value = f"```{insert_data['item']}```")
		else:
			embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']} → {insert_data['item']}```")
		if jungsan_data['toggle'] == insert_data['toggle']:
			embed.add_field(name = "[ 루팅 ]", value = f"```{insert_data['toggle']}```")
		else:
			embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']} → {insert_data['toggle']}```")
		if jungsan_data['before_jungsan_ID'] == insert_data['before_jungsan_ID']:
			embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(insert_data['before_jungsan_ID'])}```")
		else:
			embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID'])} → {', '.join(insert_data['before_jungsan_ID'])}```")
		embed.set_footer(text = f"{insert_data['modifydate'].strftime('%Y-%m-%d %H:%M:%S')} 수정!")
		await ctx.send(embed = embed)

		data_regist_warning_message = await ctx.send(f"**입력하신 수정 내역을 확인해 보세요!**\n**수정 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 수정이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await data_regist_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == data_regist_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **수정**을 취소합니다!")

		if str(reaction) == "⭕":
			result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":insert_data}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 등록 내역 수정 실패.") 

			return await ctx.send(f"📥 정산 등록 내역 수정 완료! 📥")
		else:
			return await ctx.send(f"**수정**이 취소되었습니다.\n")

	################ 등록삭제 ################ 
	@commands.command(name="!등록삭제")
	async def distribute_delete(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번]** 양식으로 확인 해주세요")

		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"regist":str(ctx.author.id)}, {"_id":int(args)}, {"$or" : [{"itemstatus" : "분배완료"}, {"itemstatus" : "미판매"}]}]})

		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 분배중 ]**이거나 없습니다. **[ !등록확인 ]** 명령을 통해 확인해주세요.")
		
		embed = discord.Embed(
					title = "⚠️☠️⚠️ 삭제 내역 ⚠️☠️⚠️",
					description = "",
					color=0x00ff00
					)
		embed.add_field(name = "[ 순번 ]", value = f"```{jungsan_data['_id']}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{jungsan_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']}```")
		embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']}```")
		embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']}```")
		embed.add_field(name = "[ 상태 ]", value = f"```{jungsan_data['itemstatus']}```")
		embed.add_field(name = "[ 판매금 ]", value = f"```{jungsan_data['price']}```")
		embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID']+jungsan_data['after_jungsan_ID'])}```")
		await ctx.send(embed = embed)
		
		delete_warning_message = await ctx.send(f"**등록 내역을 삭제하시면 다시는 복구할 수 없습니다. 정말로 삭제하시겠습니까?**\n**삭제 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 삭제가 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **삭제**를 취소합니다!")

		if str(reaction) == "⭕":
			self.jungsan_db.delete_one({"_id":int(args)})
			return await ctx.send(f"☠️ 정산 내역 삭제 완료! ☠️")
		else:
			return await ctx.send(f"**삭제**가 취소되었습니다.\n")

	################ 루팅자 ################ 
	@commands.command(name="!루팅확인")
	async def loot_distribute_check(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		visual_flag : int = 0

		jungsan_document : list = []
		if not args:
			jungsan_document : list = list(self.jungsan_db.find({"toggle_ID":str(ctx.author.id)}))
		else:
			input_distribute_all_finish : list = args.split()
			
			if input_distribute_all_finish[0] == "상세":
				visual_flag = 1
				del(input_distribute_all_finish[0])
			
			len_input_distribute_all_finish = len(input_distribute_all_finish)

			if len_input_distribute_all_finish == 0:
				jungsan_document : list = list(self.jungsan_db.find({"toggle_ID":str(ctx.author.id)}))
			elif len_input_distribute_all_finish != 2:
				return await ctx.send(f"**명령어 (상세) [검색조건] [검색값]** 형식으로 입력 해주세요! **[검색조건]**은 **[순번, 보스명, 아이템, 날짜, 분배상태]** 다섯가지 중 **1개**를 입력 하셔야합니다!")
			else:
				if input_distribute_all_finish[0] == "순번":
					try:
						input_distribute_all_finish[1] = int(input_distribute_all_finish[1])
					except:
						return await ctx.send(f"**[순번] [검색값]**은 \"숫자\"로 입력 해주세요!")
					jungsan_document : list = list(self.jungsan_db.find({"toggle_ID":str(ctx.author.id), "_id":input_distribute_all_finish[1]}))
				elif input_distribute_all_finish[0] == "보스명":
					jungsan_document : list = list(self.jungsan_db.find({"toggle_ID":str(ctx.author.id), "boss":input_distribute_all_finish[1]}))
				elif input_distribute_all_finish[0] == "아이템":
					jungsan_document : list = list(self.jungsan_db.find({"toggle_ID":str(ctx.author.id), "item":input_distribute_all_finish[1]}))
				elif input_distribute_all_finish[0] == "날짜":
					try:
						start_search_date : str = datetime.datetime.now().replace(year = int(input_distribute_all_finish[1][:4]), month = int(input_distribute_all_finish[1][5:7]), day = int(input_distribute_all_finish[1][8:10]), hour = 0, minute = 0, second = 0)
						end_search_date : str = start_search_date + datetime.timedelta(days = 1)
					except:
						return await ctx.send(f"**[날짜] [검색값]**은 0000-00-00 형식으로 입력 해주세요!")
					jungsan_document : list = list(self.jungsan_db.find({"toggle_ID":str(ctx.author.id), "getdate":{"$gte":start_search_date, "$lt":end_search_date}}))
				elif input_distribute_all_finish[0] == "분배상태":
					if input_distribute_all_finish[1] == "분배중":
						jungsan_document : list = list(self.jungsan_db.find({"toggle_ID":str(ctx.author.id), "itemstatus" : "분배중"}))
					elif input_distribute_all_finish[1] == "미판매":
						jungsan_document : list = list(self.jungsan_db.find({"toggle_ID":str(ctx.author.id), "itemstatus" : "미판매"}))
					else:
						return await ctx.send(f"**[분배상태] [검색값]**은 \"미판매\" 혹은 \"분배중\"로 입력 해주세요!")
				else:
					return await ctx.send(f"**[검색조건]**이 잘못 됐습니다. **[검색조건]**은 **[순번, 보스명, 아이템, 날짜, 분배상태]** 다섯가지 중 **1개**를 입력 하셔야합니다!")
		
		if len(jungsan_document) == 0:
			return await ctx.send(f"{ctx.author.mention}님! 루팅한 정산 목록이 없습니다.")

		total_distribute_money : int = 0
		embed_list : list = []
		embed_limit_checker : int = 0
		embed_cnt : int = 0
		detail_title_info	: str = ""
		detail_info	: str = ""
		
		embed = discord.Embed(
					title = f"===== [{member_data['game_ID']}]님 루팅 내역 =====",
					description = "",
					color=0x00ff00
					)
		embed_list.append(embed)
		for jungsan_data in jungsan_document:
			embed_limit_checker += 1
			if embed_limit_checker == 20:
				embed_limit_checker = 0
				embed_cnt += 1
				tmp_embed = discord.Embed(
					title = "",
					description = "",
					color=0x00ff00
					)
				embed_list.append(tmp_embed)
			
			if jungsan_data['gulid_money_insert']:
				if jungsan_data['itemstatus'] == "미판매":
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | 혈비적립예정"
					detail_info = f"```fix\n[ 혈비적립 ]```"
				else:
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | 혈비적립완료"
					detail_info = f"~~```fix\n[ 혈비적립 ]```~~"
			elif jungsan_data['bank_money_insert']:
				detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | 은행저축"
				detail_info = f"```fix\n[ 은행저축 ]```"
			else:			
				if jungsan_data['itemstatus'] == "분배중":
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | {jungsan_data['itemstatus']} : 1인당 💰{jungsan_data['each_price']}"
					if visual_flag == 0:
						detail_info = f"```fix\n[ 분배중 ] : {len(jungsan_data['before_jungsan_ID'])}명   [ 분배완료 ] : {len(jungsan_data['after_jungsan_ID'])}명```"
					else:
						detail_info = f"```diff\n+ 분 배 중 : {len(jungsan_data['before_jungsan_ID'])}명 (💰{len(jungsan_data['before_jungsan_ID'])*jungsan_data['each_price']})\n{', '.join(jungsan_data['before_jungsan_ID'])}\n- 분배완료 : {len(jungsan_data['after_jungsan_ID'])}명  (💰{len(jungsan_data['after_jungsan_ID'])*jungsan_data['each_price']})\n{', '.join(jungsan_data['after_jungsan_ID'])}```"
					total_distribute_money += len(jungsan_data['before_jungsan_ID'])*int(jungsan_data['each_price'])
				elif jungsan_data['itemstatus'] == "미판매":
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | {jungsan_data['itemstatus']}"
					if visual_flag == 0:
						detail_info = f"```ini\n[ 참여자 ] : {len(jungsan_data['before_jungsan_ID'])}명```"
					else:
						detail_info = f"```ini\n[ 참여자 ] : {len(jungsan_data['before_jungsan_ID'])}명\n{', '.join(jungsan_data['before_jungsan_ID'])}```"
				else:
					detail_title_info = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | {jungsan_data['itemstatus']} | 💰~~{jungsan_data['price']}~~"
					if visual_flag == 0:
						detail_info = f"~~```yaml\n[ 분배완료 ] : {len(jungsan_data['after_jungsan_ID'])}명```~~"
					else:
						detail_info = f"~~```yaml\n[ 분배완료 ] : {len(jungsan_data['after_jungsan_ID'])}명\n{', '.join(jungsan_data['after_jungsan_ID'])}```~~"

			embed_list[embed_cnt].add_field(name = detail_title_info,
							value = detail_info,
							inline = False)

		if len(embed_list) > 2:
			for embed_data in embed_list:
				await ctx.send(embed = embed_data)
		else:
			await ctx.send(embed = embed)

		embed1 = discord.Embed(
			title = f"총 정산 금액 : 💰 {str(total_distribute_money)}",
			description = "",
			color=0x00ff00
			)
		return await ctx.send(embed = embed1)

	################ 루팅내역수정 ################ 
	@commands.command(name="!루팅수정")
	async def loot_modify_regist_data(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [보스명] [아이템명] [루팅자] [참여자1] [참여자2]...** 양식으로 등록 해주세요")
		
		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data < 5:
			return await ctx.send(f"**명령어 [순번] [보스명] [아이템명] [루팅자] [참여자1] [참여자2]...** 양식으로 등록 해주세요")
		
		jungsan_data : dict = self.jungsan_db.find_one({"_id":int(input_regist_data[0]), "toggle_ID":str(member_data['_id']), "itemstatus":"미판매"})
		
		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 루팅하신 정산 내역이 **[ 미판매 ]**중이 아니거나 없습니다. **[ !루팅확인 ]** 명령을 통해 확인해주세요.\n※루팅수정은 **[ 분배상태 ]**가 **[ 미판매 ]** 중인 루팅건만 수정 가능합니다!")

		del(input_regist_data[0])

		check_member_data : list = {}
		check_member_list : list = []
		check_member_id_list : list = []
		wrong_input_id : list = []
		gulid_money_insert_check : bool = False
		loot_member_data : dict = {}

		if input_regist_data[2] == "혈비":
			gulid_money_insert_check = True
			loot_member_data["_id"] = ctx.author.id
		else:
			gulid_money_insert_check = False
			loot_member_data = self.member_db.find_one({"game_ID":input_regist_data[2]})
			if not loot_member_data:
				return await ctx.send(f"```루팅자 [{input_regist_data[2]}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")

		check_member_data = list(self.member_db.find())
		for game_id in check_member_data:
			check_member_list.append(game_id['game_ID'])
			if game_id['game_ID'] == input_regist_data[2]:
				loot_member_data["_id"] = game_id['_id']

		for game_id in input_regist_data[3:]:
			if game_id not in check_member_list:
				wrong_input_id.append(game_id)
		
		if len(wrong_input_id) > 0:
			return await ctx.send(f"```참여자 [{', '.join(wrong_input_id)}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")
		
		input_time : datetime = datetime.datetime.now()
		insert_data : dict = {}
		insert_data = {"regist":jungsan_data['regist'],
					"getdate":jungsan_data['getdate'],
					"boss":input_regist_data[0],
					"item":input_regist_data[1],
					"toggle":input_regist_data[2],
					"toggle_ID":str(loot_member_data["_id"]),
					"itemstatus":"미판매",
					"price":0,
					"each_price":0,
					"before_jungsan_ID":list(set(input_regist_data[3:])),
					"after_jungsan_ID":[],
					"modifydate":input_time,
					"gulid_money_insert":gulid_money_insert_check,
					"bank_money_insert":jungsan_data["bank_money_insert"]
					}
		
		embed = discord.Embed(
				title = "===== 수정 정보 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = "[ 순번 ]", value = f"```{jungsan_data['_id']}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{jungsan_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		if jungsan_data['boss'] == insert_data['boss']:
			embed.add_field(name = "[ 보스 ]", value = f"```{insert_data['boss']}```")
		else:
			embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']} → {insert_data['boss']}```")
		if jungsan_data['item'] == insert_data['item']:
			embed.add_field(name = "[ 아이템 ]", value = f"```{insert_data['item']}```")
		else:
			embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']} → {insert_data['item']}```")
		if jungsan_data['toggle'] == insert_data['toggle']:
			embed.add_field(name = "[ 루팅 ]", value = f"```{insert_data['toggle']}```")
		else:
			embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']} → {insert_data['toggle']}```")
		if jungsan_data['before_jungsan_ID'] == insert_data['before_jungsan_ID']:
			embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(insert_data['before_jungsan_ID'])}```")
		else:
			embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID'])} → {', '.join(insert_data['before_jungsan_ID'])}```")
		embed.set_footer(text = f"{insert_data['modifydate'].strftime('%Y-%m-%d %H:%M:%S')} 수정!")
		await ctx.send(embed = embed)

		data_regist_warning_message = await ctx.send(f"**입력하신 수정 내역을 확인해 보세요!**\n**수정 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 수정이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await data_regist_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == data_regist_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **수정**을 취소합니다!")

		if str(reaction) == "⭕":
			result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":insert_data}, upsert = True)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 내역 수정 실패.") 

			return await ctx.send(f"📥 정산 내역 수정 완료! 📥")
		else:
			return await ctx.send(f"**수정**이 취소되었습니다.\n")

	################ 루팅삭제 ################ 
	@commands.command(name="!루팅삭제")
	async def loot_distribute_delete(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번]** 양식으로 확인 해주세요")

		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"toggle_ID":str(ctx.author.id)}, {"_id":int(args)}, {"$or" : [{"itemstatus" : "분배완료"}, {"itemstatus" : "미판매"}]}]})

		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 분배중 ]**이거나 없습니다. **[ !등록확인 ]** 명령을 통해 확인해주세요.")
		
		embed = discord.Embed(
					title = "⚠️☠️⚠️ 삭제 내역 ⚠️☠️⚠️",
					description = "",
					color=0x00ff00
					)
		embed.add_field(name = "[ 순번 ]", value = f"```{jungsan_data['_id']}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{jungsan_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']}```")
		embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']}```")
		embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']}```")
		embed.add_field(name = "[ 상태 ]", value = f"```{jungsan_data['itemstatus']}```")
		embed.add_field(name = "[ 판매금 ]", value = f"```{jungsan_data['price']}```")
		embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID']+jungsan_data['after_jungsan_ID'])}```")
		await ctx.send(embed = embed)
		
		delete_warning_message = await ctx.send(f"**정산 내역을 삭제하시면 다시는 복구할 수 없습니다. 정말로 삭제하시겠습니까?**\n**삭제 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 삭제가 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await delete_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == delete_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **삭제**를 취소합니다!")

		if str(reaction) == "⭕":
			self.jungsan_db.delete_one({"_id":int(args)})
			return await ctx.send(f"☠️ 정산 내역 삭제 완료! ☠️")
		else:
			return await ctx.send(f"**삭제**가 취소되었습니다.\n")

	################ 보스수정 ################ 
	@commands.command(name="!보스수정")
	async def modify_regist_boss_data(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [보스명]** 양식으로 등록 해주세요")
		
		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data != 2:
			return await ctx.send(f"**명령어 [순번] [보스명]** 양식으로 등록 해주세요")
		
		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"$or" : [{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_regist_data[0])}, {"itemstatus":"미판매"}]})
		
		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 미판매 ]**중이 아니거나 없습니다. **[ !등록확인/!루팅확인 ]** 명령을 통해 확인해주세요.\n※등록내용 수정은 **[ 분배상태 ]**가 **[ 미판매 ]** 중인 등록건만 수정 가능합니다!")

		if jungsan_data['boss'] == input_regist_data[1]:
			return await ctx.send(f"```수정하려는 [보스명:{input_regist_data[1]}](이)가 등록된 [보스명]과 같습니다!```")
		
		input_time : datetime = datetime.datetime.now()
		insert_data : dict = {}
		insert_data = jungsan_data.copy()
		insert_data["boss"] = input_regist_data[1]
		insert_data["modifydate"] = input_time
		
		embed = discord.Embed(
				title = "===== 수정 정보 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = "[ 순번 ]", value = f"```{jungsan_data['_id']}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{jungsan_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']} → {insert_data['boss']}```")
		embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']}```")
		embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']}```")
		embed.add_field(name = "[ 상태 ]", value = f"```{jungsan_data['itemstatus']}```")
		embed.add_field(name = "[ 판매금 ]", value = f"```{jungsan_data['price']}```")
		embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID'])}```")
		embed.set_footer(text = f"{insert_data['modifydate'].strftime('%Y-%m-%d %H:%M:%S')} 수정!")
		await ctx.send(embed = embed)

		data_regist_warning_message = await ctx.send(f"**입력하신 수정 내역을 확인해 보세요!**\n**수정 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 수정이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await data_regist_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == data_regist_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **수정**을 취소합니다!")

		if str(reaction) == "⭕":
			result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":insert_data}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 등록 내역 수정 실패.") 

			return await ctx.send(f"📥 정산 등록 내역 수정 완료! 📥")
		else:
			return await ctx.send(f"**수정**이 취소되었습니다.\n")

	################ 템수정 ################ 
	@commands.command(name="!템수정")
	async def modify_regist_item_data(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [아이템명]** 양식으로 등록 해주세요")
		
		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data != 2:
			return await ctx.send(f"**명령어 [순번] [아이템명]** 양식으로 등록 해주세요")
		
		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"$or" : [{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_regist_data[0])}, {"itemstatus":"미판매"}]})
		
		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 미판매 ]**중이 아니거나 없습니다. **[ !등록확인/!루팅확인 ]** 명령을 통해 확인해주세요.\n※등록내용 수정은 **[ 분배상태 ]**가 **[ 미판매 ]** 중인 등록건만 수정 가능합니다!")

		if jungsan_data['item'] == input_regist_data[1]:
			return await ctx.send(f"```수정하려는 [아이템명:{input_regist_data[1]}](이)가 등록된 [아이템명]과 같습니다!```")
		
		input_time : datetime = datetime.datetime.now()
		insert_data : dict = {}
		insert_data = jungsan_data.copy()
		insert_data["item"] = input_regist_data[1]
		insert_data["modifydate"] = input_time
		
		embed = discord.Embed(
				title = "===== 수정 정보 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = "[ 순번 ]", value = f"```{jungsan_data['_id']}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{jungsan_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']}```")
		embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']} → {insert_data['item']}```")
		embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']}```")
		embed.add_field(name = "[ 상태 ]", value = f"```{jungsan_data['itemstatus']}```")
		embed.add_field(name = "[ 판매금 ]", value = f"```{jungsan_data['price']}```")
		embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID'])}```")
		embed.set_footer(text = f"{insert_data['modifydate'].strftime('%Y-%m-%d %H:%M:%S')} 수정!")
		await ctx.send(embed = embed)

		data_regist_warning_message = await ctx.send(f"**입력하신 수정 내역을 확인해 보세요!**\n**수정 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 수정이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await data_regist_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == data_regist_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **수정**을 취소합니다!")

		if str(reaction) == "⭕":
			result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":insert_data}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 등록 내역 수정 실패.") 

			return await ctx.send(f"📥 정산 등록 내역 수정 완료! 📥")
		else:
			return await ctx.send(f"**수정**이 취소되었습니다.\n")

	################ 토글수정 ################ 
	@commands.command(name="!토글수정")
	async def modify_regist_toggle_data(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 등록 해주세요")
		
		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data != 2:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 등록 해주세요")
		
		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"$or" : [{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_regist_data[0])}, {"itemstatus":"미판매"}]})
		
		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 미판매 ]**중이 아니거나 없습니다. **[ !등록확인/!루팅확인 ]** 명령을 통해 확인해주세요.\n※등록내용 수정은 **[ 분배상태 ]**가 **[ 미판매 ]** 중인 등록건만 수정 가능합니다!")

		if jungsan_data['toggle'] == input_regist_data[1]:
			return await ctx.send(f"```수정하려는 [토글자:{input_regist_data[1]}](이)가 등록된 [토글자]과 같습니다!```")

		check_member_data : list = {}
		gulid_money_insert_check : bool = False
		loot_member_data : dict = {}

		if input_regist_data[1] == "혈비":
			gulid_money_insert_check = True
			loot_member_data["_id"] = ctx.author.id
		else:
			gulid_money_insert_check = False
			loot_member_data = self.member_db.find_one({"game_ID":input_regist_data[1]})
			if not loot_member_data:
				return await ctx.send(f"```루팅자 [{input_regist_data[1]}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")

		check_member_data = list(self.member_db.find())
		for game_id in check_member_data:
			if game_id['game_ID'] == input_regist_data[1]:
				loot_member_data["_id"] = game_id['_id']
		
		input_time : datetime = datetime.datetime.now()
		insert_data : dict = {}
		insert_data = jungsan_data.copy()
		insert_data["toggle"] = input_regist_data[1]
		insert_data["toggle_ID"] = str(loot_member_data["_id"])
		insert_data["gulid_money_insert"] = gulid_money_insert_check
		insert_data["modifydate"] = input_time

		embed = discord.Embed(
				title = "===== 수정 정보 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = "[ 순번 ]", value = f"```{jungsan_data['_id']}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{jungsan_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']}```")
		embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']}```")
		embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']} → {insert_data['toggle']}```")
		embed.add_field(name = "[ 상태 ]", value = f"```{jungsan_data['itemstatus']}```")
		embed.add_field(name = "[ 판매금 ]", value = f"```{jungsan_data['price']}```")
		embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID'])}```")
		embed.set_footer(text = f"{insert_data['modifydate'].strftime('%Y-%m-%d %H:%M:%S')} 수정!")
		await ctx.send(embed = embed)

		data_regist_warning_message = await ctx.send(f"**입력하신 수정 내역을 확인해 보세요!**\n**수정 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 수정이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await data_regist_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == data_regist_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **수정**을 취소합니다!")

		if str(reaction) == "⭕":
			result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":insert_data}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 등록 내역 수정 실패.") 

			return await ctx.send(f"📥 정산 등록 내역 수정 완료! 📥")
		else:
			return await ctx.send(f"**수정**이 취소되었습니다.\n")

	################ 참여자추가 ################ 
	@commands.command(name="!참여자추가")
	async def modify_regist_add_member_data(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 등록 해주세요")
		
		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data != 2:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 등록 해주세요")
		
		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"$or" : [{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_regist_data[0])}, {"itemstatus":"미판매"}]})
		
		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 미판매 ]**중이 아니거나 없습니다. **[ !등록확인/!루팅확인 ]** 명령을 통해 확인해주세요.\n※등록내용 수정은 **[ 분배상태 ]**가 **[ 미판매 ]** 중인 등록건만 수정 가능합니다!")

		if input_regist_data[1] in jungsan_data['before_jungsan_ID']:
			return await ctx.send(f"```수정하려는 [참여자:{input_regist_data[1]}](이)가 등록된 [참여자] 목록에 있습니다!```")

		check_member_data : dict = {}

		tmp_member_list : list = []

		check_member_data = self.member_db.find_one({"game_ID":input_regist_data[1]})
		if not check_member_data:
			return await ctx.send(f"```참여자 [{input_regist_data[1]}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")
		
		tmp_member_list = jungsan_data["before_jungsan_ID"].copy()
		tmp_member_list.append(check_member_data["game_ID"])

		input_time : datetime = datetime.datetime.now()
		insert_data : dict = {}
		insert_data = jungsan_data.copy()
		insert_data["before_jungsan_ID"] = tmp_member_list

		embed = discord.Embed(
				title = "===== 수정 정보 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = "[ 순번 ]", value = f"```{jungsan_data['_id']}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{jungsan_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']}```")
		embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']}```")
		embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']}```")
		embed.add_field(name = "[ 상태 ]", value = f"```{jungsan_data['itemstatus']}```")
		embed.add_field(name = "[ 판매금 ]", value = f"```{jungsan_data['price']}```")
		embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID'])} → {', '.join(insert_data['before_jungsan_ID'])}```")
		embed.set_footer(text = f"{insert_data['modifydate'].strftime('%Y-%m-%d %H:%M:%S')} 수정!")
		await ctx.send(embed = embed)

		data_regist_warning_message = await ctx.send(f"**입력하신 수정 내역을 확인해 보세요!**\n**수정 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 수정이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await data_regist_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == data_regist_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **수정**을 취소합니다!")

		if str(reaction) == "⭕":
			result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":insert_data}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 등록 내역 수정 실패.") 

			return await ctx.send(f"📥 정산 등록 내역 수정 완료! 📥")
		else:
			return await ctx.send(f"**수정**이 취소되었습니다.\n")

	################ 참여자삭제 ################ 
	@commands.command(name="!참여자삭제")
	async def modify_regist_remove_member_data(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 등록 해주세요")
		
		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data != 2:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 등록 해주세요")
		
		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"$or" : [{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_regist_data[0])}, {"itemstatus":"미판매"}]})
		
		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 미판매 ]**중이 아니거나 없습니다. **[ !등록확인/!루팅확인 ]** 명령을 통해 확인해주세요.\n※등록내용 수정은 **[ 분배상태 ]**가 **[ 미판매 ]** 중인 등록건만 수정 가능합니다!")

		if input_regist_data[1] not in jungsan_data['before_jungsan_ID']:
			return await ctx.send(f"```수정하려는 [참여자:{input_regist_data[1]}](이)가 등록된 [참여자] 목록에 없습니다!```")

		check_member_data : dict = {}

		tmp_member_list : list = []

		check_member_data = self.member_db.find_one({"game_ID":input_regist_data[1]})
		if not check_member_data:
			return await ctx.send(f"```참여자 [{input_regist_data[1]}](은)는 혈원으로 등록되지 않은 아이디 입니다.```")
		
		tmp_member_list = jungsan_data["before_jungsan_ID"].copy()
		tmp_member_list.remove(check_member_data["game_ID"])

		if len(tmp_member_list) <= 0:
			return await ctx.send(f"```참여자 [{input_regist_data[1]}]를 삭제하면 참여자가 [0]명이 되므로 삭제할 수 없습니다!```")

		input_time : datetime = datetime.datetime.now()
		insert_data : dict = {}
		insert_data = jungsan_data.copy()
		insert_data["before_jungsan_ID"] = tmp_member_list

		embed = discord.Embed(
				title = "===== 수정 정보 =====",
				description = "",
				color=0x00ff00
				)
		embed.add_field(name = "[ 순번 ]", value = f"```{jungsan_data['_id']}```", inline = False)
		embed.add_field(name = "[ 일시 ]", value = f"```{jungsan_data['getdate'].strftime('%Y-%m-%d %H:%M:%S')}```", inline = False)
		embed.add_field(name = "[ 보스 ]", value = f"```{jungsan_data['boss']}```")
		embed.add_field(name = "[ 아이템 ]", value = f"```{jungsan_data['item']}```")
		embed.add_field(name = "[ 루팅 ]", value = f"```{jungsan_data['toggle']}```")
		embed.add_field(name = "[ 상태 ]", value = f"```{jungsan_data['itemstatus']}```")
		embed.add_field(name = "[ 판매금 ]", value = f"```{jungsan_data['price']}```")
		embed.add_field(name = "[ 참여자 ]", value = f"```{', '.join(jungsan_data['before_jungsan_ID'])} → {', '.join(insert_data['before_jungsan_ID'])}```")
		embed.set_footer(text = f"{insert_data['modifydate'].strftime('%Y-%m-%d %H:%M:%S')} 수정!")
		await ctx.send(embed = embed)

		data_regist_warning_message = await ctx.send(f"**입력하신 수정 내역을 확인해 보세요!**\n**수정 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 수정이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await data_regist_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == data_regist_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **수정**을 취소합니다!")

		if str(reaction) == "⭕":
			result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":insert_data}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 등록 내역 수정 실패.") 

			return await ctx.send(f"📥 정산 등록 내역 수정 완료! 📥")
		else:
			return await ctx.send(f"**수정**이 취소되었습니다.\n")

	################ 판매입력 ################ 
	@commands.command(name="!판매")
	async def input_sell_price(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [금액]** 양식으로 입력 해주세요")
		
		input_sell_price_data : list = args.split()
		len_input_sell_price_data = len(input_sell_price_data)

		if len_input_sell_price_data != 2:
			return await ctx.send(f"**명령어 [순번] [금액]** 양식으로 입력 해주세요")
		
		try:
			input_sell_price_data[0] = int(input_sell_price_data[0])
			input_sell_price_data[1] = int(input_sell_price_data[1])
		except ValueError:
			return await ctx.send(f"**[순번]** 및 **[금액]**은 숫자로 입력 해주세요")

		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"$or" : [{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_sell_price_data[0])}, {"itemstatus":"미판매"}]})

		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 미판매 ]** 중이 아니거나 없습니다. **[ !등록확인 ]** 명령을 통해 확인해주세요")

		result_each_price = int(input_sell_price_data[1]//len(jungsan_data["before_jungsan_ID"]))

		if jungsan_data["gulid_money_insert"]:
			result = self.jungsan_db.update_one({"_id":input_sell_price_data[0]}, {"$set":{"price":input_sell_price_data[1], "each_price":result_each_price, "before_jungsan_ID":[], "after_jungsan_ID":jungsan_data["before_jungsan_ID"], "itemstatus":"분배완료"}}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 혈비 등록 실패.")
			result_guild = self.guild_db.update_one({"_id":"guild"}, {"$inc":{"guild_money":input_sell_price_data[1]}}, upsert = True)
			if result_guild.raw_result["nModified"] < 1 and "upserted" not in result_guild.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 혈비 적립 실패.")
			return await ctx.send(f"**[ 순번 : {input_sell_price_data[0]} ]**   💰판매금 **[ {input_sell_price_data[1]} ]** 혈비 적립 완료!")
		
		result = self.jungsan_db.update_one({"_id":input_sell_price_data[0]}, {"$set":{"price":input_sell_price_data[1], "each_price":result_each_price, "itemstatus":"분배중"}}, upsert = False)
		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
			return await ctx.send(f"{ctx.author.mention}, 판매 등록 실패.") 			

		return await ctx.send(f"**[ 순번 : {input_sell_price_data[0]} ]**   💰판매금 **[ {input_sell_price_data[1]} ]** 등록 완료! 분배를 시작합니다.")

	################ 정산 처리 입력 ################ 
	@commands.command(name="!정산")
	async def distribute_finish(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 정산 해주세요")

		input_distribute_finish_data : list = args.split()
		len_input_distribute_finish_data = len(input_distribute_finish_data)

		if len_input_distribute_finish_data != 2:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 정산 해주세요")

		try:
			input_distribute_finish_data[0] = int(input_distribute_finish_data[0])
		except ValueError:
			return await ctx.send(f"**[순번]**은 숫자로 입력 해주세요")

		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"$or" : [{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_distribute_finish_data[0])}, {"itemstatus":"분배중"}]})

		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 분배중 ]**이 아니거나 없습니다. **[ !등록확인 ]** 명령을 통해 확인해주세요")
		else:
			if input_distribute_finish_data[1] in jungsan_data["after_jungsan_ID"]:
				return await ctx.send(f"**[ {input_distribute_finish_data[1]} ]**님은 **[ 순번 : {input_distribute_finish_data[0]} ]**의 정산 내역에 대하여 이미 💰**[ {jungsan_data['each_price']} ]** 정산 받았습니다!")
			elif input_distribute_finish_data[1] not in jungsan_data["before_jungsan_ID"]:
				return await ctx.send(f"**[ {input_distribute_finish_data[1]} ]**님은 **[ 순번 : {input_distribute_finish_data[0]} ]**의 정산 전 명단에 존재하지 않습니다!")
			else:
				pass
				
		jungsan_data["before_jungsan_ID"].remove(input_distribute_finish_data[1])
		jungsan_data["after_jungsan_ID"].append(input_distribute_finish_data[1])

		len_before_jungsan_data :int = 0
		len_before_jungsan_data = len(jungsan_data["before_jungsan_ID"])

		if len_before_jungsan_data == 0:
			result = self.jungsan_db.update_one({"_id":int(input_distribute_finish_data[0])}, {"$set":{"before_jungsan_ID":jungsan_data["before_jungsan_ID"], "after_jungsan_ID":jungsan_data["after_jungsan_ID"], "itemstatus" : "분배완료"}}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 실패.") 		
			return await ctx.send(f"**[ 순번 : {input_distribute_finish_data[0]} ]** : **[ {input_distribute_finish_data[1]} ]**님 정산 완료!\n**[ 순번 : {input_distribute_finish_data[0]} ]** 분배 완료!🎉")
		else:
			result = self.jungsan_db.update_one({"_id":int(input_distribute_finish_data[0])}, {"$set":{"before_jungsan_ID":jungsan_data["before_jungsan_ID"], "after_jungsan_ID":jungsan_data["after_jungsan_ID"]}}, upsert = False)
			if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
				return await ctx.send(f"{ctx.author.mention}, 정산 실패.") 		
			return await ctx.send(f"**[ 순번 : {input_distribute_finish_data[0]} ]** : **[ {input_distribute_finish_data[1]} ]**님 정산 완료!")
	
	################ 정산 처리 취소 ################ 
	@commands.command(name="!정산취소")
	async def cancel_distribute_finish(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 정산 해주세요")

		input_distribute_finish_data : list = args.split()
		len_input_distribute_finish_data = len(input_distribute_finish_data)

		if len_input_distribute_finish_data != 2:
			return await ctx.send(f"**명령어 [순번] [아이디]** 양식으로 정산 해주세요")

		try:
			input_distribute_finish_data[0] = int(input_distribute_finish_data[0])
		except ValueError:
			return await ctx.send(f"**[순번]**은 숫자로 입력 해주세요")

		jungsan_data : dict = self.jungsan_db.find_one({"$and" : [{"$or" : [{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_distribute_finish_data[0])}, {"itemstatus":"분배중"}]})

		if not jungsan_data:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 분배중 ]**이 아니거나 없습니다. **[ !등록확인 ]** 명령을 통해 확인해주세요")
		else:
			if input_distribute_finish_data[1] in jungsan_data["before_jungsan_ID"]:
				return await ctx.send(f"**[ {input_distribute_finish_data[1]} ]**님은 **[ 순번 : {input_distribute_finish_data[0]} ]**의 정산 내역에 대하여 아직 정산 받지 않았습니다!")
			elif input_distribute_finish_data[1] not in jungsan_data["after_jungsan_ID"]:
				return await ctx.send(f"**[ {input_distribute_finish_data[1]} ]**님은 **[ 순번 : {input_distribute_finish_data[0]} ]**의 정산 후 명단에 존재하지 않습니다!")
			else:
				pass
				
		jungsan_data["after_jungsan_ID"].remove(input_distribute_finish_data[1])
		jungsan_data["before_jungsan_ID"].append(input_distribute_finish_data[1])

		result = self.jungsan_db.update_one({"_id":int(input_distribute_finish_data[0])}, {"$set":{"before_jungsan_ID":jungsan_data["before_jungsan_ID"], "after_jungsan_ID":jungsan_data["after_jungsan_ID"]}}, upsert = False)
		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
			return await ctx.send(f"{ctx.author.mention}, 정산 취소 실패.") 		
		return await ctx.send(f"**[ 순번 : {input_distribute_finish_data[0]} ]** : **[ {input_distribute_finish_data[1]} ]**님 정산 취소 완료!")

	################ 일괄정산 ################ 
	@commands.command(name="!일괄정산")
	async def distribute_all_finish(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		jungsan_document : list = []

		if not args:
			jungsan_document : list = list(self.jungsan_db.find({"$and" : [{"$or":[{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"itemstatus":"분배중"}]}))
		else:
			input_distribute_all_finish : list = args.split()
			len_input_distribute_all_finish = len(input_distribute_all_finish)

			if len_input_distribute_all_finish != 2:
				return await ctx.send(f"**명령어 [검색조건] [검색값]** 형식으로 입력 해주세요! **[검색조건]**은 **[순번, 보스명, 아이템, 날짜]** 다섯가지 중 **1개**를 입력 하셔야합니다!")
			else:
				if input_distribute_all_finish[0] == "순번":
					try:
						input_distribute_all_finish[1] = int(input_distribute_all_finish[1])
					except:
						return await ctx.send(f"**[순번] [검색값]**은 숫자로 입력 해주세요!")
					jungsan_document = list(self.jungsan_db.find({"$and" : [{"$or":[{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":input_distribute_all_finish[1]}, {"itemstatus":"분배중"}]}))
				elif input_distribute_all_finish[0] == "보스명":
					jungsan_document = list(self.jungsan_db.find({"$and" : [{"$or":[{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"boss":input_distribute_all_finish[1]}, {"itemstatus":"분배중"}]}))
				elif input_distribute_all_finish[0] == "아이템":
					jungsan_document = list(self.jungsan_db.find({"$and" : [{"$or":[{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"item":input_distribute_all_finish[1]}, {"itemstatus":"분배중"}]}))
				elif input_distribute_all_finish[0] == "날짜":
					try:
						start_search_date : str = datetime.datetime.now().replace(year = int(input_distribute_all_finish[1][:4]), month = int(input_distribute_all_finish[1][5:7]), day = int(input_distribute_all_finish[1][8:10]), hour = 0, minute = 0, second = 0)
						end_search_date : str = start_search_date + datetime.timedelta(days = 1)
					except:
						return await ctx.send(f"**[날짜] [검색값]**은 0000-00-00 형식으로 입력 해주세요!")
					jungsan_document = list(self.jungsan_db.find({"$and" : [{"$or":[{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"getdate":{"$gte":start_search_date, "$lt":end_search_date}}, {"itemstatus":"분배중"}]}))
				else:
					return await ctx.send(f"**[검색조건]**이 잘못 됐습니다. **[검색조건]**은 **[순번, 보스명, 아이템, 날짜]** 네가지 중 **1개**를 입력 하셔야합니다!")

		if len(jungsan_document) == 0:
			return await ctx.send(f"{ctx.author.mention}님! **[ 분배중 ]**인 정산 내역이 없거나 등록된 정산 내역이 없습니다.")

		total_distribute_money : int = 0
		detail_info_ing : str = ""
		embed_list : list = []
		embed_limit_checker : int = 0
		embed_cnt : int = 0
		init_data : dict = {}

		embed = discord.Embed(
					title = f"===== [{member_data['game_ID']}]님 등록 내역 =====",
					description = "",
					color=0x00ff00
					)

		embed_list.append(embed)
		for jungsan_data in jungsan_document:
			embed_limit_checker += 1
			if embed_limit_checker == 20:
				embed_limit_checker = 0
				embed_cnt += 1
				tmp_embed = discord.Embed(
					title = "",
					description = "",
					color=0x00ff00
					)
				embed_list.append(tmp_embed)
			detail_info_ing = f"```diff\n+ 분 배 중 : {len(jungsan_data['before_jungsan_ID'])}명 (💰{len(jungsan_data['before_jungsan_ID'])*jungsan_data['each_price']})\n{', '.join(jungsan_data['before_jungsan_ID'])}\n- 분배완료 : {len(jungsan_data['after_jungsan_ID'])}명  (💰{len(jungsan_data['after_jungsan_ID'])*jungsan_data['each_price']})\n{', '.join(jungsan_data['after_jungsan_ID'])}```"
			embed_list[embed_cnt].add_field(name = f"[ 순번 : {jungsan_data['_id']} ] | {jungsan_data['getdate'].strftime('%Y-%m-%d')} | {jungsan_data['boss']} | {jungsan_data['item']} | {jungsan_data['toggle']} | {jungsan_data['itemstatus']} : 1인당 💰{jungsan_data['each_price']}",
							value = detail_info_ing,
							inline = False)
			total_distribute_money += len(jungsan_data['before_jungsan_ID'])*int(jungsan_data['each_price'])
			init_data[jungsan_data['_id']] = jungsan_data['after_jungsan_ID']

		if len(embed_list) > 2:
			for embed_data in embed_list:
				await ctx.send(embed = embed_data)
		else:
			await ctx.send(embed = embed)

		embed1 = discord.Embed(
			title = f"일괄정산 예정 금액 : 💰 {str(total_distribute_money)}",
			description = "",
			color=0x00ff00
			)
		await ctx.send(embed = embed1)

		distribute_all_finish_warning_message = await ctx.send(f"**일괄 정산 예정인 등록 내역을 확인해 보세요!**\n**일괄정산 : ⭕ 취소: ❌**\n(10초 동안 입력이 없을시 일괄정산이 취소됩니다.)", tts=False)

		emoji_list : list = ["⭕", "❌"]
		for emoji in emoji_list:
			await distribute_all_finish_warning_message.add_reaction(emoji)

		def reaction_check(reaction, user):
			return (reaction.message.id == distribute_all_finish_warning_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)

		try:
			reaction, user = await self.bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
		except asyncio.TimeoutError:
			for emoji in emoji_list:
				await data_regist_warning_message.remove_reaction(emoji, self.bot.user)
			return await ctx.send(f"시간이 초과됐습니다. **일괄정산**을 취소합니다!")

		if str(reaction) == "⭕":
			for jungsan_data in jungsan_document:
				result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":{"before_jungsan_ID":[], "after_jungsan_ID":init_data[jungsan_data['_id']]+jungsan_data['before_jungsan_ID'], "itemstatus":"분배완료"}}, upsert = True)
				if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
					await ctx.send(f"{ctx.author.mention}, 일괄정산 실패.") 

			return await ctx.send(f"📥 일괄정산 완료! 📥")
		else:
			return await ctx.send(f"**일괄정산**이 취소되었습니다.\n")

def setup(bot):
  bot.add_cog(manageCog(bot))


