from discord import (
	Cog, Bot, ApplicationContext
)
from discord.ext.commands import slash_command as command
from discord import option
from .functions import log
from .constants import CONST_OTHERS
from .autocomplete import AutoComplete

from uuid import uuid4
from json import dump
from os.path import isfile

class Walica(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Walica] Loading module "Walica"...')
		self.bot: Bot = bot
		log('[Walica] Module "Walica" loaded.')
		return

	# Command: /add-event
	@command(
		name = 'add-event',
		description = '新しい割り勘イベントを作成します [Module: Walica]'
	)
	async def __add_event(self, ctx: ApplicationContext) -> None:
		eventId: str = str(uuid4())
		filepath: str = '%s/.event-queue/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, eventId)
		data = {
			'eventId': eventId,
			'participants': [{
				'name': u.display_name,
				'icon': u.avatar.url,
				'id': u.id,
				'screenId': u.name
			} for u in ctx.guild.members if not u.bot],
			'returnTo': {
				'guild': ctx.guild.id,
				'channel': ctx.channel.id
			}
		}

		with open(filepath, 'w') as fp: dump(data, fp)

		await ctx.respond('%s/walica/create.php?eventId=%s' % (CONST_OTHERS.APP_URL, eventId))
	
	@command(
		name = 'add-item',
		description = '割り勘の内容を追加します [Module: Walica]'
	)
	@option(
		name = 'event_id',
		type = str,
		description = '対象のイベントID',
		autocomplete = AutoComplete.getWalicaEvent,
		required = True
	)
	async def __add_item(self, ctx: ApplicationContext, event_id: str) -> None:
		itemId: str = str(uuid4())
		filepath: str = '%s/.item-queue/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, itemId)
		
		if not isfile('%s/.events/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, event_id)):
			await ctx.respond('Error: イベントID \'%s\' は存在しません！' % event_id)
			return
		data = {
			'itemId': itemId,
			'targetEventId': event_id,
			'issuer': {
				'name': ctx.user.display_name,
				'icon': ctx.user.avatar.url,
				'id': ctx.user.id,
				'screenId': ctx.user.name
			},
			'returnTo': {
				'guild': ctx.guild.id,
				'channel': ctx.channel.id
			}
		}
		with open(filepath, 'w') as fp: dump(data, fp)

		await ctx.respond('%s/walica/add-item.php?itemId=%s' % (CONST_OTHERS.APP_URL, itemId))