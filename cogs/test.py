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
import checks, boss_utils

class testCog(commands.Cog): 
	bot_setting = discordbot_total.ilsang_total_bot

	def __init__(self, bot):
		self.bot = bot
		
		self.test_task.start()

	@tasks.loop(seconds=1.0, count=1)
	async def test_task(self):
		print("tasks")
		# test_a = asyncio.Task(self.check_func(self.bot, 677399458924855296)).set_name("test_503909372511125504")
		# test_b = asyncio.Task(self.check_func(self.bot, 696965026908471347)).set_name("test_bbb")
		# test_c = asyncio.Task(self.check_func(self.bot, 731050948620714014)).set_name("test_ccc")
		# test_d = asyncio.Task(self.check_func(self.bot, 725194772205142106)).set_name("test_ddd")
		# test_e = asyncio.Task(self.check_func(self.bot, 737123749513527346)).set_name("test_eee")
		
		# await asyncio.gather(test_a)
		# await asyncio.gather(test_a, test_b, test_c, test_d, test_e)

	async def check_func(self, bot, channel):
		while True:
			await bot.get_channel(channel).send(f"{self.bot.test_text} : {datetime.datetime.now()}")
			await asyncio.sleep(0.7) 

	@test_task.before_loop
	async def before_test(self):
		await self.bot.wait_until_ready()

	@commands.command(name="테스트")
	async def command_test(self, ctx : commands.Context):
		await ctx.send("테스트")

	################ 채널등록 ################ 
	@commands.command(name="명치")
	async def command_task_list(self, ctx : commands.Context):
		for t in asyncio.Task.all_tasks():
			# print(t._coro.__name__)
			if t.get_name() == f"test_{ctx.message.guild.id}":
				print(t.get_name())
				print('정지')
				if t.done():
					try:
						t.exception()
					except asyncio.CancelledError:
						continue
					continue
				t.cancel()
		print(f"태스크 {ctx.message.guild.name} 취소")

		# test_a = asyncio.get_event_loop().create_task(self.check_func(self.bot, 696965026908471347)).set_name(f"test_{ctx.message.guild.id}")

def setup(bot):
	bot.add_cog(testCog(bot))


