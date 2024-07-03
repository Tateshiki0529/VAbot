from extensions.functions import log, is_owner
from extensions.versions import VersionInfo
from extensions.autocomplete import AutoComplete
from extensions.constants import CONST_ENV, CONST_OTHERS, CONST_DATE

from emoji import emojize
from datetime import datetime as dt, timezone as tz, timedelta as td
from os.path import getmtime, isfile
from discord import (
	Cog, Bot, Intents, ApplicationContext, Embed
)
from discord import option
from discord.ext.commands import (
	slash_command as command
)

class SlashFixV4(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Core] Loading module "Core"...')
		self.bot: Bot = bot
		log('[Core] Loading extensions...')
		self.bot.load_extension('extensions.debug')
		self.bot.load_extension('extensions.images')
		self.bot.load_extension('extensions.trolls')
		self.bot.load_extension('extensions.gomamayo')
		self.bot.load_extension('extensions.traininfo')
		self.bot.load_extension('extensions.weather')
		# await self.bot.load_extension(Earthquake(bot=bot))
		self.bot.load_extension('extensions.math')
		self.bot.load_extension('extensions.walica')
		self.bot.load_extension('extensions.voice')
		self.bot.load_extension('extensions.voicevox')
		self.bot.load_extension('extensions.music')
		self.bot.load_extension('extensions.cssearch')
		log('[Core] All extensions loaded.')
		log('[Core] Module "Core" loaded.')
		return
	
	@Cog.listener()
	async def on_ready(self) -> None:
		log("[Core] %s#%s: Bot is ready!" % (self.bot.user.display_name, self.bot.user.discriminator))
		# self.bot.cogs['Earthquake'].connect()
		return

	@Cog.listener()
	async def on_application_command(self, ctx: ApplicationContext) -> None:
		log("[Core] %s@%s issued: /%s" % (ctx.user.display_name, ctx.user.name, ctx.command.qualified_name))
		return
	
	@Cog.listener()
	async def on_disconnect(self) -> None:
		log("[Core] Connection closed. Bot stopped.")
		return
	
	@command(
		name = 'reload',
		description = 'モジュールをリロードします [Module: Core] [Admin]'
	)
	@option(
		name = 'module_name',
		type = str,
		description = 'リロードするモジュール名',
		autocomplete = AutoComplete.getModules
	)
	async def __reload(self, ctx: ApplicationContext, module_name: str) -> None:
		if not is_owner(ctx):
			await ctx.respond('Error: このコマンドは管理者以外使用できません。')
			return
		if isfile('./modules/%s.py' % module_name): self.bot.reload_extension()

	# Command: /version [version]
	@command(
		name = 'version',
		description = 'Botのバージョン情報を返します [Module: Core]',
		aliases = ['ver']
	)
	@option(
		name = 'version',
		type = str,
		description = '参照するバージョン',
		required = False,
		autocomplete = AutoComplete.getVersion
	)
	async def __version(self, ctx: ApplicationContext, version: str = None) -> None:
		if not version:
			embed = Embed(
				title='V.A.Bot Version %s' % VersionInfo.version,
				color=0x91e3f9,
				timestamp=dt.now().astimezone(tz(td(hours=9)))
			)

			embed.set_author(
				name = CONST_OTHERS.BOT_NAME,
				icon_url = CONST_OTHERS.BOT_ICON_URL
			)
			embed.add_field(
				name = 'バージョン',
				value = VersionInfo.version,
				inline = True
			)
			embed.add_field(
				name = '最終更新日',
				value = dt.fromtimestamp(getmtime('./extensions/versions.py')).astimezone(tz(td(hours=9))).strftime(CONST_DATE.FORMAT),
				inline = True
			)
			embed.add_field(
				name = '最新の更新内容',
				value = VersionInfo.description[VersionInfo.version],
				inline = False
			)
		else:
			embed = Embed(
				title='V.A.Bot Version %s' % version,
				color=0x91e3f9,
				timestamp=dt.now().astimezone(tz(td(hours=9)))
			)
			embed.set_author(
				name = CONST_OTHERS.BOT_NAME,
				icon_url = CONST_OTHERS.BOT_ICON_URL
			)
			embed.add_field(
				name = 'バージョン',
				value = version,
				inline = True
			)
			embed.add_field(
				name = '更新内容',
				value = VersionInfo.description[version],
				inline = False
			)
		embed.set_footer(text='%s@%s issued: /version' % (ctx.author.display_name, ctx.author.name), icon_url=ctx.author.display_avatar.url)

		await ctx.respond(embed=embed)
		return
	
	# Command: /stop-server
	@command(
		name = 'stop-server',
		description = 'Botを停止します [Module: Core] [Admin]'
	)
	async def __stop_server(self, ctx: ApplicationContext) -> None:
		if not is_owner(ctx):
			await ctx.respond('Error: このコマンドは管理者以外使用できません。')
			return
		await ctx.respond(emojize(':wave:'))
		cogs = [c for c in self.bot.cogs]
		for cog in cogs:
			self.bot.remove_cog(cog)
		await self.bot.close()
		return

	

if __name__ == '__main__':
	log('[System] Initializing...')
	bot = Bot(auto_sync_commands=True, intents=Intents().all(), debug_guilds=[CONST_OTHERS.GUILD_ID])

	log('[System] Loading module "Core"...')
	bot.add_cog(SlashFixV4(bot=bot))
	log('[System] Module loaded.')
	log('[System] Starting...')
	bot.run(CONST_ENV.DISCORD_SUB_TOKEN)