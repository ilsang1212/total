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
import discordbot_jungsan
import checks, utils

class testCog(commands.Cog): 
	bot_setting = discordbot_jungsan.ilsang_distribution_bot

	def __init__(self, bot):
		self.bot = bot

		self.test_task.start()

	@tasks.loop(seconds=1.0, count=1)
	async def test_task(self):
		test_a = asyncio.Task(self.check_func(self.bot, 725194772205142106)).set_name("test_aaa")
		# test_b = self.check_func(self.bot, 737123749513527346)
		# test_c = self.check_func(self.bot, 725194772205142106)
		# test_d = self.check_func(self.bot, 731050948620714014)
		# test_e = self.check_func(self.bot, 696965026908471347)
		
		await asyncio.gather(test_a)
		# await asyncio.gather(test_a, test_b, test_c, test_d, test_e)

	async def check_func(self, bot, channel):
		while True:
			await bot.get_channel(channel).send(f"{channel} : {datetime.datetime.now()}")
			await asyncio.sleep(0.7) 

	@test_task.before_loop
	async def before_test(self):
		await self.bot.wait_until_ready()

	################ 채널등록 ################ 
	@commands.command(name="태스크")
	async def command_task_list(self, ctx : commands.Context):
		for t in asyncio.Task.all_tasks():
			print(t._coro.__name__)
			if t._coro.__name__ == "check_func":
				print(t)
				if t.done():
					try:
						t.exception()
					except asyncio.CancelledError:
						continue
					continue
				t.cancel()
		print("태스크 다시시작")
		test_a = asyncio.get_event_loop().create_task(self.check_func(self.bot, 737123749513527346))

def setup(bot):
	bot.add_cog(testCog(bot))


