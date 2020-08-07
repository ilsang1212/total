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

#서버(길드) 정보 
def get_guild_channel_info(bot):
	guild_info : list = []
	guild_channel_info : dict = {}
	text_channel_name : list = []
	text_channel_id : list = []
	voice_channel_name : list = []
	voice_channel_id : list = []
	
	for guild in bot.guilds:
		guild_info.append(guild)
		text_channel_name = []
		text_channel_id = []
		voice_channel_name = []
		voice_channel_id = []
		for text_channel in guild.text_channels:
			text_channel_name.append(text_channel.name)
			text_channel_id.append(str(text_channel.id))
		for voice_channel in guild.voice_channels:
			voice_channel_name.append(voice_channel.name)
			voice_channel_id.append(str(voice_channel.id))
		guild_channel_info[str(guild.id)] = {
			"guild_name" : guild.name,
			"text_channel_name_info" : text_channel_name,
			"text_channel_id_info" : text_channel_id,
			"voice_channel_name_info" : voice_channel_name,
			"voice_channel_id_info" : voice_channel_id
			}

	return guild_info, guild_channel_info

#보스 정보 추출
def get_boss_data(filename : str, repo):
	bossNum : int = 0
	result : list = []
	tmp_bossData : list = []
	boss_data : dict = {}

	boss_info_inidata = repo.get_contents(filename)
	boss_file_data = base64.b64decode(boss_info_inidata.content)
	boss_file_data = boss_file_data.decode('utf-8')
	boss_info_inidata = boss_file_data.split('\n')

	for i in range(boss_info_inidata.count('')):
		boss_info_inidata.remove('')

	if  "----- 일반보스 -----" in boss_info_inidata[0]:
		del(boss_info_inidata[0])
		bossNum = int(len(boss_info_inidata)/5)

		for j in range(bossNum):
			tmp_bossData.append(boss_info_inidata[j*5:j*5+5])
			for i in range(len(tmp_bossData[j])):
				tmp_bossData[j][i] = tmp_bossData[j][i].strip()
	
		for i in range(bossNum):
			boss_data = {}
			boss_data["_id"] = tmp_bossData[i][0][tmp_bossData[i][0].find("=")+2:].rstrip('\r')
			boss_data["gentime"] = tmp_bossData[i][1][tmp_bossData[i][1].find("=")+2:].rstrip('\r')
			boss_data["nogenchk"] = tmp_bossData[i][2][tmp_bossData[i][2].find("=")+2:].rstrip('\r')
			boss_data["before_alert_ment"] = tmp_bossData[i][3][tmp_bossData[i][3].find("=")+2:].rstrip('\r')
			boss_data["alert_ment"] = tmp_bossData[i][4][tmp_bossData[i][4].find("=")+2:].rstrip('\r')
			result.append(boss_data)
	else:
		del(boss_info_inidata[0])
		bossNum = int(len(boss_info_inidata)/6)

		for j in range(bossNum):
			tmp_bossData.append(boss_info_inidata[j*6:j*6+6])
			for i in range(len(tmp_bossData[j])):
				tmp_bossData[j][i] = tmp_bossData[j][i].strip()
	
		for i in range(bossNum):
			boss_data = {}
			boss_data["_id"] = tmp_bossData[i][0][tmp_bossData[i][0].find("=")+2:].rstrip('\r')
			boss_data["bosstime"] = tmp_bossData[i][1][tmp_bossData[i][1].find("=")+2:].rstrip('\r')
			boss_data["genPeriod"] = tmp_bossData[i][2][tmp_bossData[i][2].find("=")+2:].rstrip('\r')
			boss_data["startDate"] = tmp_bossData[i][3][tmp_bossData[i][3].find("=")+2:].rstrip('\r')
			boss_data["before_alert_ment"] = tmp_bossData[i][4][tmp_bossData[i][4].find("=")+2:].rstrip('\r')
			boss_data["alert_ment"] = tmp_bossData[i][5][tmp_bossData[i][5].find("=")+2:].rstrip('\r')
			result.append(boss_data)

	return result

	#보스 정보 입력
def set_boss_data(boss_info_db : list, flag : str = "boss", timezone : int = 9):
	result : list = []
	tmp_dict : dict = {}
	if flag == "boss":
		for boss_info in boss_info_db:
			tmp_dict = {}
			tmp_dict[boss_info["_id"]] = boss_info.copy()
			tmp_dict[boss_info["_id"]]["bossTime"] = datetime.datetime.now() + datetime.timedelta(days=365, hours = timezone)
			tmp_dict[boss_info["_id"]]["tmp_bossTime"] = datetime.datetime.now() + datetime.timedelta(days=365, hours = timezone)
			tmp_dict[boss_info["_id"]]["bossTimeString"] = "99:99:99"
			tmp_dict[boss_info["_id"]]["bossDateString"] = "9999-99-99"
			tmp_dict[boss_info["_id"]]["tmp_bossTimeString"] = "99:99:99"
			tmp_dict[boss_info["_id"]]["tmp_bossDateString"] = "9999-99-99"
			tmp_dict[boss_info["_id"]]["bossFlag"] = False
			tmp_dict[boss_info["_id"]]["bossFlag0"] = False
			tmp_dict[boss_info["_id"]]["bossMungFlag"] = False
			tmp_dict[boss_info["_id"]]["bossMungCnt"] = 0
			tmp_dict[boss_info["_id"]]["bossNick"] = boss_info["_id"],
			tmp_dict[boss_info["_id"]]["bossUse"] = True
			del (tmp_dict[boss_info["_id"]]["_id"])
			result.append(tmp_dict)
	else:
		for boss_info in boss_info_db:
			tmp_dict = {}
			tmp_fixed_now = datetime.datetime.now() + datetime.timedelta(hours = timezone)
			tmp_fixed_len = boss_info["bosstime"].find(':')
			tmp_fixed_gen_len = boss_info["genPeriod"].find(':')
			tmp_dict[boss_info["_id"]] = boss_info.copy()
			tmp_dict[boss_info["_id"]]["bossName"] = boss_info["_id"]
			tmp_dict[boss_info["_id"]]["bossNick"] = boss_info["_id"][:boss_info["_id"].find("_")]
			tmp_dict[boss_info["_id"]]["bossUse"] = True,
			tmp_dict[boss_info["_id"]]["fixed_bossFlag"] = False
			tmp_dict[boss_info["_id"]]["fixed_bossFlag0"] = False
			tmp_dict[boss_info["_id"]]["fixed_bossTime"] = tmp_fixed_now.replace(year = int(tmp_dict[boss_info["_id"]]["startDate"][0:4]), month = int(tmp_dict[boss_info["_id"]]["startDate"][5:7]), day = int(tmp_dict[boss_info["_id"]]["startDate"][8:10]), hour=int(tmp_dict[boss_info["_id"]]["bosstime"][0:tmp_fixed_len]), minute=int(tmp_dict[boss_info["_id"]]["bosstime"][tmp_fixed_len+1:]), second = int(0))
			if tmp_dict[boss_info["_id"]]["fixed_bossTime"] < tmp_fixed_now :
				while tmp_dict[boss_info["_id"]]["fixed_bossTime"] < tmp_fixed_now :
					tmp_dict[boss_info["_id"]]["fixed_bossTime"] = tmp_dict[boss_info["_id"]]["fixed_bossTime"] + datetime.timedelta(hours=int(tmp_dict[boss_info["_id"]]["genPeriod"][0:tmp_fixed_gen_len]), minutes=int(tmp_dict[boss_info["_id"]]["genPeriod"][tmp_fixed_gen_len+1:]), seconds = int(0))
			del (tmp_dict[boss_info["_id"]]["_id"])
			result.append(tmp_dict)

	return result

#mp3 파일 생성함수(gTTS 이용, 남성목소리)
async def MakeSound(saveSTR, filename):
	
	tts = gTTS(saveSTR, lang = 'ko')
	tts.save('./' + filename + '.wav')

#mp3 파일 재생함수	
async def PlaySound(voiceclient, filename):
	source = discord.FFmpegPCMAudio(filename)
	try:
		voiceclient.play(source)
	except discord.errors.ClientException:
		while voiceclient.is_playing():
			await asyncio.sleep(1)
	while voiceclient.is_playing():
		await asyncio.sleep(1)
	voiceclient.stop()
	source.cleanup()