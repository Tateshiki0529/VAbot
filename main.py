from modules.functions import log, is_owner
from modules.versions import VersionInfo
from modules.autocomplete import AutoComplete
from modules.constants import CONST_ENV, CONST_OTHERS, CONST_DATE

from modules.debug import Debug
from modules.images import Images
from modules.trolls import Trolls
from modules.gomamayo import Gomamayo
from modules.traininfo import TrainInfo
from modules.weather import Weather
from modules.earthquake import Earthquake
from modules.math import Math
from modules.walica import Walica
from modules.voice import Voice

from emoji import emojize
from datetime import datetime as dt, timezone as tz, timedelta as td
from os.path import getmtime
from discord import (
	Cog, Bot, Intents, ApplicationContext, Embed
)
from discord import option
from discord.ext.commands import (
	slash_command as command
)

class SlashFixV4(Cog):
	def __init__(self, bot: Bot) -> None:
		self.bot: Bot = bot
		log('[Core] Loading modules...')
		self.bot.add_cog(Debug(bot=bot))
		self.bot.add_cog(Images(bot=bot))
		self.bot.add_cog(Trolls(bot=bot))
		self.bot.add_cog(Gomamayo(bot=bot))
		self.bot.add_cog(TrainInfo(bot=bot))
		self.bot.add_cog(Weather(bot=bot))
		self.bot.add_cog(Earthquake(bot=bot))
		self.bot.add_cog(Math(bot=bot))
		self.bot.add_cog(Walica(bot=bot))
		self.bot.add_cog(Voice(bot=bot))
		log('[Core] All modules loaded.')
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
				name = '@S.U.S.VictimsAssociation',
				icon_url = 'https://tests.ttsk3.net/images/icon.png'
			)
			embed.add_field(
				name = 'バージョン',
				value = VersionInfo.version,
				inline = True
			)
			embed.add_field(
				name = '最終更新日',
				value = dt.fromtimestamp(getmtime('./modules/versions.py')).astimezone(tz(td(hours=9))).strftime(CONST_DATE.FORMAT),
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
				name = '@S.U.S.VictimsAssociation',
				icon_url = 'https://tests.ttsk3.net/images/icon.png'
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
	
	# Command: /stop
	@command(
		name = 'stop',
		description = 'Botを停止します [Module: Core] [Admin]'
	)
	async def __stop(self, ctx: ApplicationContext) -> None:
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
	bot.run(CONST_ENV.DISCORD_TOKEN)