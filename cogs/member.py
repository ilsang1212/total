from discord.ext import commands
import discord
import checks
import discordbot_jungsan

class memberCog(commands.Cog): 
	commandSetting : list = discordbot_jungsan.ilsang_distribution_bot.commandSetting

	def __init__(self, bot):
		self.bot = bot	

		self.member_db = self.bot.db.jungsan.member
		self.jungsan_db = self.bot.db.jungsan.jungsandata
		self.guild_db = self.bot.db.jungsan.guild

	################ 총무등록 ################ 
	@commands.has_permissions(manage_guild=True)
	@commands.command(name="!총무등록", aliases=["!ㅊㅁㄷㄹ"])
	async def set_manager(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"game_ID":args})

		if not member_data:
			return await ctx.send(f"**[{args}]**님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [아이디]** 양식으로 등록 해주세요")

		result = self.member_db.update_one({"game_ID":member_data["game_ID"]}, {"$set":{"permissions":"manager"}}, upsert = True)
		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
			return await ctx.send(f"{ctx.author.mention}, 총무 등록 실패.")   

		return  await ctx.send(f"**[{args}]**님을 총무로 등록 하였습니다.")

	################ 총무삭제 ################ 
	@commands.has_permissions(manage_guild=True)
	@commands.command(name="!총무삭제", aliases=["!ㅊㅁㅅㅈ"])
	async def delete_manager(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"game_ID":args})

		if not member_data:
			return await ctx.send(f"**[{args}]**님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [아이디]** 양식으로 삭제 해주세요")

		result = self.member_db.update_one({"game_ID":member_data["game_ID"]}, {"$set":{"permissions":"member"}}, upsert = True)
		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
			return await ctx.send(f"{ctx.author.mention}, 총무 삭제 실패.")   

		return  await ctx.send(f"**[{args}]**님을 총무에서 삭제 하였습니다.")

	################ 혈원목록 확인 ################ 
	@commands.command(name="!혈원", aliases=["!ㅎㅇ"])
	async def member_list(self, ctx):
		member_data : dict = self.member_db.find_one({"_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		remain_guild_money : int = 0

		guild_data : dict = self.guild_db.find_one({"_id":"guild"})

		if not guild_data:
			remain_guild_money = 0
		else:
			remain_guild_money = guild_data["guild_money"]
			
		member_list : str = ""
		cnt = 0

		for member_document in list(self.member_db.find({})):
			cnt +=1
			if member_document["permissions"] == "manager":
				member_list += f"**```md\n{cnt}.[{member_document['_id']}][{member_document['game_ID']}] 👑\n```**"
			else:
				member_list += f"```md\n{cnt}.[{member_document['_id']}][{member_document['game_ID']}]\n```"

		embed = discord.Embed(
		title = "👥  혈원 목록",
		description = member_list,
		color=0x00ff00
		)
		embed.add_field(name = f"**👤 혈원**",value = f"**```fix\n{cnt}```**")
		embed.add_field(name = f"**💰 혈비**",value = f"**```fix\n{remain_guild_money}```**")
		embed.set_footer(text = f"👑 표시는 총무!")
		return await ctx.send(embed = embed)

	################ 혈원아이디 등록 ################ 
	@commands.command(name="!혈원등록", aliases=["!ㅎㅇㄷㄹ"])
	async def member_add(self, ctx, *, args : str = None):
		if not args:
			return await ctx.send(f"**명령어 [아이디]** 양식으로 추가 해주세요")

		member_document : dict = self.member_db.find_one({ "_id":ctx.author.id})
		member_game_ID_document : dict = self.member_db.find_one({ "game_ID":args})

		if member_document:
			return await ctx.send(f"```이미 등록되어 있습니다!```")

		if member_game_ID_document:
			return await ctx.send(f"```이미 등록된 [아이디]입니다!```")

		result = self.member_db.update_one({"_id":ctx.author.id}, {"$set":{"game_ID":args, "discord_name":self.bot.get_user(ctx.author.id).display_name, "permissions":"member", "account":0}}, upsert = True)

		# "_id" : int = discord_ID
		# "game_ID" : str = game_ID
		# "discord_name" : str = discord_nickname
		# "permissiotns" : str = 권한 ["manager", "member"]
		# "account" : int = 은행잔고

		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
			return await ctx.send(f"{ctx.author.mention}, 혈원 등록 실패.")   

		return await ctx.send(f"{ctx.author.mention}님! **[{args}] [{ctx.author.id}]**(으)로 혈원 등록 완료!")

	################ 혈원아이디 수정 ################ 
	@commands.command(name="!혈원수정", aliases=["!ㅎㅇㅅㅈ"])
	async def member_modify(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({ "_id":ctx.author.id})

		if not member_data:
			return await ctx.send(f"{ctx.author.mention}님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [아이디]** 양식으로 수정 해주세요")

		jungsan_document = list(self.jungsan_db.find({"$and" : [{"$or" : [{"before_jungsan_ID" : member_data['game_ID']}, {"after_jungsan_ID" : member_data['game_ID']}]}, {"$or" : [{"itemstatus" : "분배중"}, {"itemstatus" : "미판매"}]}]}))
		len_jungsan_document : int = len(jungsan_document)
		
		if len_jungsan_document != 0:
			for jungsan_data in jungsan_document:
				if member_data['game_ID'] in jungsan_data["before_jungsan_ID"]:
					jungsan_data["before_jungsan_ID"].remove(member_data['game_ID'])
					jungsan_data["before_jungsan_ID"].append(args)
					result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":{"before_jungsan_ID":jungsan_data["before_jungsan_ID"]}}, upsert = False)
				else:
					jungsan_data["after_jungsan_ID"].remove(member_data['game_ID'])
					jungsan_data["after_jungsan_ID"].append(args)
					result = self.jungsan_db.update_one({"_id":jungsan_data['_id']}, {"$set":{"after_jungsan_ID":jungsan_data["after_jungsan_ID"]}}, upsert = False)

		result = self.member_db.update_one({"_id":ctx.author.id}, {"$set":{"game_ID":args}}, upsert = True)
		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
			return await ctx.send(f"{ctx.author.mention}, 아이디 수정 실패.")   

		return await ctx.send(f"{ctx.author.mention}님, 아이디를 **[{member_data['game_ID']}]**에서 **[{args}]**로 변경하였습니다.")

	################ 혈원아이디 등록 ################ 
	@checks.is_manager()
	@commands.command(name="!혈원입력", aliases=["!ㄹ"])
	async def member_input_add(self, ctx, *, args : str = None):
		if not args:
			return await ctx.send(f"**명령어 [아이디] [디코ID]** 양식으로 추가 해주세요")

		input_regist_data : list = args.split()
		len_input_regist_data = len(input_regist_data)

		if len_input_regist_data < 2:
			return await ctx.send(f"**명령어 [아이디] [디코ID]** 양식으로 추가 해주세요")

		member_document : dict = self.member_db.find_one({ "_id":input_regist_data[1]})
		member_game_ID_document : dict = self.member_db.find_one({ "game_ID":input_regist_data[0]})

		if member_document:
			return await ctx.send(f"```이미 등록되어 있습니다!```")

		if member_game_ID_document:
			return await ctx.send(f"```이미 등록된 [ 아이디 ] 입니다!```")

		result = self.member_db.update_one({"_id":input_regist_data[1]}, {"$set":{"game_ID":input_regist_data[0], "discord_name":self.bot.get_user(int(input_regist_data[1])).display_name, "permissions":"member", "account":0}}, upsert = True)
		if result.raw_result["nModified"] < 1 and "upserted" not in result.raw_result:
			return await ctx.send(f"**[{input_regist_data[0]}] [{input_regist_data[1]}]**(으)로 혈원 등록 실패.")   

		return await ctx.send(f"**[{input_regist_data[0]}] [{input_regist_data[1]}]**(으)로 혈원 등록 완료!")

	################ 혈원아이디 삭제 ################ 
	@checks.is_manager()
	@commands.command(name="!혈원삭제", aliases=["!ㅎㅇㅈㄱ"])
	async def member_delete(self, ctx, *, args : str = None):
		member_data : dict = self.member_db.find_one({"game_ID":args})

		if not member_data:
			return await ctx.send(f"**[{args}]**님은 혈원으로 등록되어 있지 않습니다!")

		if not args:
			return await ctx.send(f"**명령어 [아이디]** 양식으로 삭제 해주세요")

		jungsan_document = list(self.jungsan_db.find({"before_jungsan_ID" : args, "itemstatus" : "분배중"}))
		len_jungsan_document : int = len(jungsan_document)
		
		if len_jungsan_document != 0:
			remain_jungsan_info : str = ""
			total_remain_money : int = 0
			for jungsan_data in jungsan_document:
				total_remain_money += jungsan_data['each_price']
				remain_jungsan_info += f"**[ 순번 : {jungsan_data['_id']}]** 💰 {jungsan_data['each_price']}\n"

			await ctx.send(f"```잔여정산 목록이 있어 혈원을 삭제할 수 없습니다.```")
			embed = discord.Embed(
				title = "===== 잔여 졍산 목록 =====",
				description = remain_jungsan_info,
				color=0x00ff00
				)
			embed.add_field(name = "\u200b", value = f"잔여 정산 금액 : 💰 {total_remain_money}")
			return await ctx.send(embed = embed)

		result = self.member_db.delete_one({"game_ID":args})
		
		return  await ctx.send(f"**[{args}]**님을 혈원에서 삭제 하였습니다.")

def setup(bot):
  bot.add_cog(memberCog(bot))


