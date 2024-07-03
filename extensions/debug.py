from discord import (
	Cog, Bot, ApplicationContext
)
from discord import option
from discord.ext.commands import (
	slash_command as command
)
from .functions import log

class Debug(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Debug] Loading module "Debug"...')
		self.bot: Bot = bot
		log('[Debug] Module "Debug" loaded.')
		return
	
	# Command: /view-variables <variable_name>
	@command(
		name = 'view-variables',
		description = '変数を表示します [Module: Debug]',
		aliases = ['viewvar']
	)
	@option(
		name = 'variable_name',
		description = '変数の名前',
		required = True,
		type = str
	)
	async def __view_variables(self, ctx: ApplicationContext, variable_name: str) -> None:
		try:
			await ctx.respond('`%s`: `%s`' % (variable_name, eval(variable_name)))
		except NameError:
			await ctx.respond('Error: 変数 `%s` は定義されていません！' % variable_name)
		
		return

# ----------------------------

def setup(bot: Bot):
	bot.add_cog(Debug(bot=bot))