import discord

#서버(길드) 정보 
def get_guild_channel_info(bot):
	guild_info : list = []
	text_channel_name : list = []
	text_channel_id : list = []
	voice_channel_name : list = []
	voice_channel_id : list = []
	
	for guild in bot.guilds:
		guild_info.append(guild)
		for text_channel in guild.text_channels:
			text_channel_name.append(text_channel.name)
			text_channel_id.append(str(text_channel.id))
		for voice_channel in guild.voice_channels:
			voice_channel_name.append(voice_channel.name)
			voice_channel_id.append(str(voice_channel.id))

	return guild_info, text_channel_name, text_channel_id, voice_channel_name, voice_channel_id

#detail embed
def get_detail_embed(info : dict = {}):
	embed = discord.Embed(
			title = "📜 등록 정보",
			description = "",
			color=0x00ff00
			)
	embed.add_field(name = "[ 순번 ]", value = f"```{info['_id']}```")
	embed.add_field(name = "[ 등록 ]", value = f"```{info['regist']}```")
	embed.add_field(name = "[ 일시 ]", value = f"```{info['getdate'].strftime('%y-%m-%d %H:%M:%S')}```", inline = False)
	embed.add_field(name = "[ 보스 ]", value = f"```{info['boss']}```")
	embed.add_field(name = "[ 아이템 ]", value = f"```{info['item']}```")
	embed.add_field(name = "[ 루팅 ]", value = f"```{info['toggle']}```")
	embed.add_field(name = "[ 상태 ]", value = f"```{info['itemstatus']}```")
	embed.add_field(name = "[ 판매금 ]", value = f"```{info['price']}```")
	if info['before_jungsan_ID']:
		embed.add_field(name = "[ 정산전 ]", value = f"```{', '.join(info['before_jungsan_ID'])}```", inline = False)
	if info['after_jungsan_ID']:
		embed.add_field(name = "[ 정산후 ]", value = f"```{', '.join(info['after_jungsan_ID'])}```")
	if 'image_url' in info.keys():
		if info['image_url'] is not None:
			embed.set_image(url = info['image_url'])
	return embed