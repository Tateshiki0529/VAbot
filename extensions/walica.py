from discord import (
	Cog, Bot, ApplicationContext, Member, Embed
)
from discord.ext.commands import slash_command as command
from discord import option, Color
from .functions import log
from .constants import CONST_OTHERS, CONST_DATE
from .autocomplete import AutoComplete

from datetime import datetime as dt
from uuid import uuid4
from json import dump, load
from os.path import isfile
from os import remove

class Walica(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Walica] Loading extension "Walica"...')
		self.bot: Bot = bot
		log('[Walica] Extension "Walica" loaded.')
		return

	# Command: /add-event
	@command(
		name = 'add-event',
		description = '新しい割り勘イベントを作成します [Extension: Walica]'
	)
	async def __add_event(self, ctx: ApplicationContext) -> None:
		eventId: str = str(uuid4())
		filepath: str = '%s/.event-queue/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, eventId)
		data = {
			'eventId': eventId,
			'eventIssuer': {
				'name': ctx.user.display_name,
				'icon': ctx.user.avatar.url,
				'id': ctx.user.id,
				'screenId': ctx.user.name
			},
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
		return
	
	@command(
		name = 'add-item',
		description = '割り勘の内容を追加します [Extension: Walica]'
	)
	@option(
		name = 'event_id',
		type = str,
		description = '対象のイベントID',
		autocomplete = AutoComplete.getWalicaEvent,
		required = True
	)
	@option(
		name = 'for_user',
		type = Member,
		description = '立て替えしたメンバー',
		required = False
	)
	async def __add_item(self, ctx: ApplicationContext, event_id: str, for_user: Member | None = None) -> None:
		if not for_user:
			user_info = {
				'name': ctx.user.display_name,
				'icon': ctx.user.avatar.url,
				'id': ctx.user.id,
				'screenId': ctx.user.name
			}
		else:
			user_info = {
				'name': for_user.display_name,
				'icon': for_user.avatar.url,
				'id': for_user.id,
				'screenId': for_user.name
			}
		itemId: str = str(uuid4())
		filepath: str = '%s/.item-queue/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, itemId)
		
		if not isfile('%s/.events/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, event_id)):
			await ctx.respond('Error: イベントID `%s` は存在しません！' % event_id)
			return
		data = {
			'itemId': itemId,
			'targetEventId': event_id,
			'issuer': user_info,
			'returnTo': {
				'guild': ctx.guild.id,
				'channel': ctx.channel.id
			}
		}
		with open(filepath, 'w') as fp: dump(data, fp)

		await ctx.respond('%s/walica/add-item.php?itemId=%s' % (CONST_OTHERS.APP_URL, itemId))
		return

	@command(
		name = 'remove-item',
		description = '割り勘の内容を削除します [Extension: Walica]'
	)
	@option(
		name = 'event_id',
		type = str,
		description = '対象のイベントID',
		autocomplete = AutoComplete.getWalicaEvent,
		required = True
	)
	@option(
		name = 'item_id',
		type = str,
		description = '対象の項目ID',
		autocomplete = AutoComplete.getWalicaItem,
		required = True
	)
	async def __remove_item(self, ctx: ApplicationContext, event_id: str, item_id: str) -> None:
		filepath = '%s/.events/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, event_id)
		if not isfile(filepath):
			await ctx.respond('Error: イベントID `%s` は存在しません！' % event_id)
			return
		itemData: dict = None
		with open(filepath, 'r') as fp:
			eventData = load(fp)
		for v in eventData['eventCostDetails']:
			if v['itemId'] == item_id:
				itemData = v
		if not itemData:
			await ctx.respond('Error: 項目ID `%s` は存在しません！' % item_id)
			return

		if itemData['itemIssuer']['id'] != ctx.user.id:
			await ctx.respond('Error: 登録した人しか削除できません！')
			return
		newItemList = []
		for v in eventData['eventCostDetails']:
			if v['itemId'] != item_id:
				newItemList.append(v)
		
		eventData['eventCostDetails'] = newItemList

		with open(filepath, 'w') as fp: dump(eventData, fp)

		await ctx.respond('項目 `%s` を削除しました！' % itemData['itemName'])
		return
	
	@command(
		name = 'remove-event',
		description = '割り勘イベントを削除します [Extension: Walica]'
	)
	@option(
		name = 'event_id',
		type = str,
		description = '対象のイベントID',
		autocomplete = AutoComplete.getWalicaEvent,
		required = True
	)
	async def __remove_event(self, ctx: ApplicationContext, event_id: str) -> None:
		filepath = '%s/.events/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, event_id)
		if not isfile(filepath):
			await ctx.respond('Error: イベントID `%s` は存在しません！' % event_id)
			return
		with open(filepath, 'r') as fp:
			eventData = load(fp)

		if eventData['eventIssuer']['id'] != ctx.user.id:
			await ctx.respond('Error: 作成した人しか削除できません！')
			return
		
		remove(filepath)
		await ctx.respond('イベント `%s` を削除しました！' % eventData['eventName'])
		return
	
	@command(
		name = 'view-payment',
		description = '誰に払うかを確認します [Extension: Walica]'
	)
	@option(
		name = 'event_id',
		type = str,
		description = '対象のイベントID',
		autocomplete = AutoComplete.getWalicaEvent,
		required = True
	)
	@option(
		name = 'target_user',
		type = Member,
		description = '対象のメンバー',
		required = False
	)
	async def __view_payment(self, ctx: ApplicationContext, event_id: str, target_user: Member | None = None) -> None:
		if not target_user:
			target_user: Member = ctx.user
		
		filepath = '%s/.events/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, event_id)
		if not isfile(filepath):
			await ctx.respond('Error: イベントID `%s` は存在しません！' % event_id)
			return
		with open(filepath, 'r') as fp:
			eventData = load(fp)

		payments = []
		totalCost = 0
		for payment in eventData['eventCostDetails']:
			if str(target_user.id) in payment['targets'].keys():
				payments.append({
					'itemId': payment['itemId'],
					'itemName': payment['itemName'],
					'from': str(target_user.id),
					'to': str(payment['itemIssuer']['id']),
					'cost': payment['targets'][str(target_user.id)]
				})
				totalCost += payment['targets'][str(target_user.id)]

		embed = Embed(title='支払い詳細', color=Color.from_rgb(140, 255, 140))
		embed.set_author(
			name = CONST_OTHERS.BOT_NAME,
			icon_url = CONST_OTHERS.BOT_ICON_URL
		)
		embed.description = 'イベント: %s (EventID: %s)' % (eventData['eventName'], eventData['eventId'])
		if len(payments) == 0:
			embed.add_field(name='項目なし', value='支払う項目がありません！', inline=False)
		else:
			for payment in payments:
				if payment['from'] == payment['to']:
					embed.add_field(name='%s (PaymentID: %s)' % (payment['itemName'], payment['itemId']), value='<@%s>: `¥ %s`' % (payment['to'], format(payment['cost'], ',')), inline=False)
				else:
					embed.add_field(name='%s (PaymentID: %s)' % (payment['itemName'], payment['itemId']), value='<@%s> → <@%s>: `¥ %s`' % (payment['from'], payment['to'], format(payment['cost'], ',')), inline=False)
		embed.add_field(name='合計金額', value='`¥ %s`' % (format(totalCost, ',')), inline=False)
		embed.timestamp = dt.now()
		embed.set_footer(text='%s@%s issued: /view-payment' % (ctx.author.display_name, ctx.author.name), icon_url=ctx.author.display_avatar.url)
		await ctx.respond(embed=embed)
		return
	
	@command(
		name = 'view-item',
		description = '特定の項目を確認します [Extension: Walica]'
	)
	@option(
		name = 'event_id',
		type = str,
		description = '対象のイベントID',
		autocomplete = AutoComplete.getWalicaEvent,
		required = True
	)
	@option(
		name = 'item_id',
		type = str,
		description = '対象のアイテムID',
		required = True,
		autocomplete = AutoComplete.getWalicaItem
	)
	async def __view_item(self, ctx: ApplicationContext, event_id: str, item_id: str) -> None:
		filepath = '%s/.events/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, event_id)
		if not isfile(filepath):
			await ctx.respond('Error: イベントID `%s` は存在しません！' % event_id)
			return
		with open(filepath, 'r') as fp:
			eventData = load(fp)
		
		itemData: dict = None
		for v in eventData['eventCostDetails']:
			if v['itemId'] == item_id:
				itemData = v
		if not itemData:
			await ctx.respond('Error: 項目ID `%s` は存在しません！' % item_id)
			return

		embed = Embed(title='項目詳細', color=Color.from_rgb(140, 255, 140))
		embed.set_author(
			name = CONST_OTHERS.BOT_NAME,
			icon_url = CONST_OTHERS.BOT_ICON_URL
		)
		details = []
		for tKey, tVal in itemData['targets'].items():
			if str(itemData['itemIssuer']['id']) != tKey:
				details.append('<@%s> → <@%s>: `¥ %s`' % (tKey, itemData['itemIssuer']['id'], format(tVal, ',')))
			else:
				details.append('<@%s>: `¥ %s`' % (itemData['itemIssuer']['id'], format(tVal, ',')))

		embed.description = 'イベント: %s (EventID: %s)' % (eventData['eventName'], eventData['eventId'])
		embed.add_field(name='項目名', value=itemData['itemName'], inline=True)
		embed.add_field(name='項目ID', value=itemData['itemId'], inline=True)
		embed.add_field(name='立て替えた人', value='<@%s>' % itemData['itemIssuer']['id'], inline=True)
		embed.add_field(name='作成日時', value=dt.fromtimestamp(itemData['itemCreatedAt']).strftime(CONST_DATE.FORMAT), inline=True)
		embed.add_field(name='かかった金額', value='`¥ %s`' % format(itemData['itemCost'], ','), inline=True)
		embed.add_field(name='割り勘詳細', value='\n'.join(details), inline=False)
		embed.timestamp = dt.now()
		embed.set_footer(text='%s@%s issued: /view-item' % (ctx.author.display_name, ctx.author.name), icon_url=ctx.author.display_avatar.url)
		await ctx.respond(embed=embed)
		return
	
	@command(
		name = 'view-event',
		description = '特定のイベントを確認します [Extension: Walica]'
	)
	@option(
		name = 'event_id',
		type = str,
		description = '対象のイベントID',
		autocomplete = AutoComplete.getWalicaEvent,
		required = True
	)
	async def __view_event(self, ctx: ApplicationContext, event_id: str) -> None:
		filepath = '%s/.events/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, event_id)
		if not isfile(filepath):
			await ctx.respond('Error: イベントID `%s` は存在しません！' % event_id)
			return
		with open(filepath, 'r') as fp:
			eventData = load(fp)

		embed = Embed(title='割り勘イベント詳細', color=Color.from_rgb(140, 255, 140))
		embed.set_author(
			name = CONST_OTHERS.BOT_NAME,
			icon_url = CONST_OTHERS.BOT_ICON_URL
		)

		embed.add_field(name='イベント名', value=eventData['eventName'], inline=True)
		embed.add_field(name='イベントID', value=eventData['eventId'], inline=True)
		embed.add_field(name='作成者', value='<@%s>' % eventData['eventIssuer']['id'], inline=True)
		embed.add_field(name='作成日時', value=dt.fromtimestamp(eventData['eventCreatedAt']).strftime(CONST_DATE.FORMAT), inline=True)
		embed.add_field(name='参加者', value=' '.join(['<@%s>' % p['id'] for p in eventData['eventParticipants']]), inline=True)
		embed.add_field(name='項目一覧', value='\n'.join(['・%s by <@%s> `(¥ %s)`' % (p['itemName'], p['itemIssuer']['id'], format(p['itemCost'], ',')) for p in eventData['eventCostDetails']]), inline=False)
		embed.timestamp = dt.now()
		embed.set_footer(text='%s@%s issued: /view-event' % (ctx.author.display_name, ctx.author.name), icon_url=ctx.author.display_avatar.url)
		await ctx.respond(embed=embed)
		return

# ----------------------------

def setup(bot: Bot):
	bot.add_cog(Walica(bot=bot))