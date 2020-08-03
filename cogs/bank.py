from discord.ext import commands
import discord
import checks
import discordbot_jungsan

class bankCog(commands.Cog): 
	commandSetting : list = discordbot_jungsan.ilsang_distribution_bot.commandSetting

	def __init__(self, bot):
		self.bot = bot	

		self.member_db = self.bot.db.jungsan.member
		self.jungsan_db = self.bot.db.jungsan.jungsandata
		self.guild_db = self.bot.db.jungsan.guild

	################ 수수료 계산기 ################ 
	@commands.command(name="!수수료", aliases=["!ㅅㅅㄹ"])
	async def tax_check(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")
		
		input_money_data : list = args.split()
		len_input_money_data = len(input_money_data)

		try:
			for i in range(len_input_money_data):
				input_money_data[i] = int(input_money_data[i])
		except ValueError:
			return await ctx.send(f"**명령어 [판매금액] (서버거래소세금)** 양식으로 입력 해주세요\n※ 서버거래소세금은 미입력시 **[ 5% ]**입니다.")

		if len_input_money_data < 1 or len_input_money_data > 3:
			return await ctx.send(f"**명령어 [판매금액] (서버거래소세금)** 양식으로 입력 해주세요\n※ 서버거래소세금은 미입력시 **[ 5% ]**입니다.")
		elif len_input_money_data == 2:
			tax = input_money_data[1]
		else:
			tax = 5

		price_first_tax = int(input_money_data[0] * ((100-tax)/100))
		price_second_tax = int(price_first_tax * ((100-tax)/100))

		embed = discord.Embed(
				title = f"🧮  수수료 계산결과 (세율 {tax}% 기준) ",
				description = f"",
				color=0x00ff00
				)
		embed.add_field(name = "⚖️ 1차 거래", value = f"```등록가 : {input_money_data[0]}\n정산가 : {price_first_tax}\n세 금 : {input_money_data[0]-price_first_tax}```")
		embed.add_field(name = "⚖️ 2차 거래", value = f"```등록가 : {price_first_tax}\n정산가 : {price_second_tax}\n세 금 : {price_first_tax-price_second_tax}```")
		return await ctx.send(embed = embed)

	################ 페이백 계산기 ################ 
	@commands.command(name="!페이백", aliases=["!ㅍㅇㅂ"])
	async def payback_check(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")
		
		input_money_data : list = args.split()
		len_input_money_data = len(input_money_data)

		try:
			for i in range(len_input_money_data):
				input_money_data[i] = int(input_money_data[i])
		except ValueError:
			return await ctx.send(f"**명령어 [거래소가격] [실거래가] (거래소세금)** 양식으로 입력 해주세요\n※ 거래소세금은 미입력시 5%입니다.")

		if len_input_money_data < 2 or len_input_money_data > 4:
			return await ctx.send(f"**명령어 [거래소가격] [실거래가] (서버거래소세금)** 양식으로 입력 해주세요\n※ 거래소세금은 미입력시 5%입니다.")
		elif len_input_money_data == 3:
			tax = input_money_data[2]
		else:
			tax = 5

		price_reg_tax = int(input_money_data[0] * ((100-tax)/100))
		price_real_tax = int(input_money_data[1] * ((100-tax)/100))

		reault_payback = price_reg_tax - price_real_tax

		embed = discord.Embed(
				title = f"🧮  페이백 계산결과 (세율 {tax}% 기준) ",
				description = f"**```fix\n{reault_payback}```**",
				color=0x00ff00
				)
		embed.add_field(name = "⚖️ 거래소", value = f"```등록가 : {input_money_data[0]}\n정산가 : {price_reg_tax}\n세 금 : {input_money_data[0]-price_reg_tax}```")
		embed.add_field(name = "🕵️ 실거래", value = f"```등록가 : {input_money_data[1]}\n정산가 : {price_real_tax}\n세 금 : {input_money_data[1]-price_real_tax}```")
		return await ctx.send(embed = embed)

	################ 계좌확인 ################ 
	@commands.command(name="!계좌", aliases=["!ㄱㅈ"])
	async def account_check(self, ctx):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		embed = discord.Embed(
				title = f"[{member_data['game_ID']}]님 은행 잔고 📝",
				description = f"**```diff\n{member_data['account']}```**",
				color=0x00ff00
				)
		embed.set_thumbnail(url = ctx.author.avatar_url)
		return await ctx.send(embed = embed)

	################ 저축 ################ 
	@commands.command(name="!저축", aliases=["!ㅈㅊ"])
	async def bank_save_money(self, ctx, *, args : str = None):
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

		jungsan_document : dict = self.jungsan_db.find_one({"$and" : [{"$or":[{"toggle_ID" : str(ctx.author.id)}, {"regist" : str(ctx.author.id)}]}, {"_id":int(input_sell_price_data[0])}, {"itemstatus":"미판매"}]})
		if not jungsan_document:
			return await ctx.send(f"{ctx.author.mention}님! 등록하신 정산 내역이 **[ 미판매 ]** 중이 아니거나 없습니다. **[ !등록확인/!루팅확인 ]** 명령을 통해 확인해주세요")
		
		result_each_price : int = int(input_sell_price_data[1]//len(jungsan_document["before_jungsan_ID"]))

		participant_list : list = jungsan_document["before_jungsan_ID"]

		self.member_db.update_many({"game_ID":{"$in":participant_list}}, {"$inc":{"account":result_each_price}})

		insert_data : dict = {}
		insert_data = {
					"itemstatus":"분배완료",
					"price":input_sell_price_data[1],
					"each_price":result_each_price,
					"before_jungsan_ID":[],
					"after_jungsan_ID":jungsan_document["before_jungsan_ID"],
					"bank_money_insert":True
					}

		result = self.jungsan_db.update_one({"_id":input_sell_price_data[0]}, {"$set":insert_data}, upsert = False)
		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
			return await ctx.send(f"{ctx.author.mention}, 은행 저축 실패.")		

		return await ctx.send(f"**[ 순번 : {input_sell_price_data[0]} ]**   💰판매금 **[ {input_sell_price_data[1]} ]**  인당 **💰 [ {result_each_price} ]** 은행 저축 완료!")

	################ 입금 #################
	@checks.is_manager() 
	@commands.command(name="!입금", aliases=["!ㅇㄱ"])
	async def bank_deposit_money(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")
			
		if not args:
			return await ctx.send(f"**명령어 [금액] [아이디] [아이디]...** 양식으로 입력 해주세요")
		
		input_bank_deposit_data : list = args.split()

		input_bank_deposit_data[1:]

		try:
			input_bank_deposit_data[0] = int(input_bank_deposit_data[0])
		except ValueError:
			return await ctx.send(f"**[금액]**은 숫자로 입력 해주세요")

		result_update = self.member_db.update_many({"game_ID":{"$in":input_bank_deposit_data[1:]}}, {"$inc":{"account":input_bank_deposit_data[0]}})
		if result_update.modified_count != len(input_bank_deposit_data[1:]):
			return await ctx.send(f"```은행 입금 실패. 정확한 [아이디]를 입력 후 다시 시도 해보세요!```")

		return await ctx.send(f"```ml\n{input_bank_deposit_data[1:]}님 💰[{input_bank_deposit_data[0]}] 은행 입금 완료!.```")

	################ 출금 #################
	@checks.is_manager() 
	@commands.command(name="!출금", aliases=["!ㅊㄱ"])
	async def bank_withdraw_money(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")
			
		if not args:
			return await ctx.send(f"**명령어 [금액] [아이디] [아이디]...** 양식으로 입력 해주세요")
		
		input_bank_withdraw_data : list = args.split()

		input_bank_withdraw_data[1:]

		try:
			input_bank_withdraw_data[0] = int(input_bank_withdraw_data[0])
		except ValueError:
			return await ctx.send(f"**[금액]**은 숫자로 입력 해주세요")

		result_update = self.member_db.update_many({"game_ID":{"$in":input_bank_withdraw_data[1:]}}, {"$inc":{"account":-input_bank_withdraw_data[0]}})

		if result_update.modified_count != len(input_bank_withdraw_data[1:]):
			return await ctx.send(f"```은행 출금 실패. 정확한 [아이디]를 입력 후 다시 시도 해보세요!```")

		return await ctx.send(f"```ml\n{input_bank_withdraw_data[1:]}님 💰[{input_bank_withdraw_data[0]}] 은행 출금 완료!.```")

	################ 혈비지원 #################
	@checks.is_manager() 
	@commands.command(name="!혈비입금", aliases=["!ㅎ"])
	async def guild_support_money_save(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")
			
		if not args:
			return await ctx.send(f"**명령어 [금액]** 양식으로 입력 해주세요")

		try:
			args = int(args)
		except ValueError:
			return await ctx.send(f"**[금액]**은 숫자로 입력 해주세요")

		result_guild_update : dict = self.guild_db.update_one({"_id":"guild"}, {"$inc":{"guild_money":args}}, upsert = True)
		if result_guild_update.raw_result["nModified"] < 1 and "upserted" not in result_guild_update.raw_result:
			return await ctx.send(f"```혈비 입금 실패!```")
		total_guild_money : dict = self.guild_db.find_one({"_id":"guild"})

		embed = discord.Embed(
				title = f"💰  혈비 입금 완료",
				description = f"",
				color=0x00ff00
				)
		embed.add_field(name = f"**입금**", value = f"**```fix\n{args}```**")
		embed.add_field(name = f"**혈비**", value = f"**```fix\n{total_guild_money['guild_money']}```**")
		return await ctx.send(embed = embed)

	################ 혈비지원 #################
	@checks.is_manager() 
	@commands.command(name="!혈비지원", aliases=["!ㅎㅂㅈㅇ"])
	async def guild_support_money(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		guild_data : dict = self.guild_db.find_one({"_id":"guild"})

		if not guild_data:
			return await ctx.send(f"등록된 혈비가 없습니다!")
			
		if not args:
			return await ctx.send(f"**명령어 [금액] [아이디] *[사유]** 양식으로 입력 해주세요")
		
		input_guild_support_money_data : list = args.split(" *")
		if len(input_guild_support_money_data) != 2:
			return await ctx.send(f"**명령어 [금액] [아이디] *[사유]** 양식으로 입력 해주세요")

		input_guild_support_money_ID_data : list = input_guild_support_money_data[0].split(" ")

		try:
			input_guild_support_money_ID_data[0] = int(input_guild_support_money_ID_data[0])
		except ValueError:
			return await ctx.send(f"**[금액]**은 숫자로 입력 해주세요")

		result_update = self.member_db.update_many({"game_ID":{"$in":input_guild_support_money_ID_data[1:]}}, {"$inc":{"account":input_guild_support_money_ID_data[0]}})

		if result_update.modified_count != len(input_guild_support_money_ID_data[1:]):
			return await ctx.send(f"```혈비 지원 실패. 정확한 [아이디]를 입력 후 다시 시도 해보세요!```")

		total_support_money : int = len(input_guild_support_money_ID_data[1:]) * input_guild_support_money_ID_data[0]

		result_guild_update = self.guild_db.update_one({"_id":"guild"}, {"$inc":{"guild_money":-total_support_money}}, upsert = False)
		if result_guild_update.raw_result["nModified"] < 1 and "upserted" not in result_guild_update.raw_result:
			return await ctx.send(f"```혈비 출금 실패!```")

		embed = discord.Embed(
				title = f"🤑 혈비 지원 완료",
				description = f"```css\n[{input_guild_support_money_data[1]}] 사유로 💰[{input_guild_support_money_ID_data[0]}]씩 혈비에서 지원했습니다.```",
				color=0x00ff00
				)
		embed.add_field(name = f"**👥  명단**", value = f"**```fix\n{', '.join(input_guild_support_money_ID_data[1:])}```**")
		embed.add_field(name = f"**💰  지원금**", value = f"**```fix\n{input_guild_support_money_ID_data[0]}```**")
		return await ctx.send(embed = embed)

def setup(bot):
  bot.add_cog(bankCog(bot))


