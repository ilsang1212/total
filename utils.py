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
def get_boss_data(filename : str, repo):
	result : list = []
	tmp_bossData : list = []
	boss_data : dict = {}
	
	# bossname = 기감
	# gentime = 01:00
	# nogencheck = 0
	# before_alert_ment = 입니다
	# alert_ment = 입니다. 어여오세요

	############## 보탐 명령어 리스트 #####################
	boss_info_inidata = repo.get_contents(filename)
	boss_file_data = base64.b64decode(boss_info_inidata.content)
	boss_file_data = boss_file_data.decode('utf-8')
	boss_info_inidata = boss_file_data.split('\n')

	for i in range(boss_info_inidata.count('\r')):
		boss_info_inidata.remove('\r')

	if boss_info_inidata[0] == "----- 일반보스 -----":
		del(boss_info_inidata[0])
		bossNum = int(len(boss_info_inidata)/5)

		for j in range(bossNum):
			tmp_bossData.append(boss_info_inidata[j*5:j*5+5])
			for i in range(len(tmp_bossData[j])):
				tmp_bossData[j][i] = tmp_bossData[j][i].strip()
	
		for i in range(bossNum):
			boss_data["_id"] = tmp_bossData[i][0][tmp_bossData[i][0].find("=")+2:].rstrip('\r')
			boss_data["gentime"] = tmp_bossData[i][1][tmp_bossData[i][1].find("=")+2:].rstrip('\r')
			boss_data["nogenchk"] = tmp_bossData[i][2][tmp_bossData[i][2].find("=")+2:].rstrip('\r')
			boss_data["before_alert_ment"] = tmp_bossData[i][3][tmp_bossData[i][3].find("=")+2:].rstrip('\r')
			boss_data["alert_ment"] = tmp_bossData[i][4][tmp_bossData[i][4].find("=")+2:].rstrip('\r')
			result.append(boss_data)

	return result