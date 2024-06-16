from discord import (
	Cog, Bot, ApplicationContext
)
from discord.ext.commands import slash_command as command
from discord import option
from .functions import log

class Math(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Math] Loading module "Math"...')
		self.bot: Bot = bot
		log('[Math] Module "Math" loaded.')
		return
	
	# Command /prime <number>
	@command(
		name = 'prime',
		description = '素数を判定します [Module: Math]'
	)
	@option(
		name = 'number',
		type = int,
		description = '判定する数',
		min_value = 1
	)
	async def __prime(self, ctx: ApplicationContext, number: int) -> None:
		await ctx.defer()
		isPrime = self.___isPrime(n=number)
		match number:
			case 57:
				await ctx.respond('%s は絶対に素数です！！！\n\nhttps://ja.m.wikipedia.org/wiki/57' % number)
				return
		if isPrime:
			await ctx.respond('%s は素数です！' % number)
			return
		else:
			await ctx.respond('%s は素数ではありません！' % number)
			return
		
	def ___isPrime(self, n: int) -> bool:
		if n <= 1:
			return False
		elif n <= 3:
			return True
		elif n % 2 == 0 or n % 3 == 0:
			return False
			i = 5
		while i * i <= n:
			if n % i == 0 or n % (i + 2) == 0:
				return False
			i += 6
		return True