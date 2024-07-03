from discord import (
	Cog, Bot, OptionChoice, ApplicationContext, Embed
)
from discord import option, Color
from discord.ext.commands import slash_command as command
from requests import get
from bs4 import BeautifulSoup
from datetime import datetime as dt, timezone as tz, timedelta as td
from re import sub

from .constants import CONST_DATE, CONST_OTHERS
from .functions import log
from .autocomplete import AutoComplete

class TrainInfoData:
	LINE_IDS: dict[str, list[int]] = {
		'iida': [197, 0],
		'chuo-e': [470, 0],
		'chuo-w': [201, 202],
		'chuo-s': [470, 0],
		'shinonoi': [472, 0],
		'oito': [473, 0]
	}
	LINE_CHOICES: list[OptionChoice] = [
		OptionChoice(
			name = '中央本線(東)',
			value = 'chuo-e'
		),
		OptionChoice(
			name = '篠ノ井線',
			value = 'shinonoi',
		),
		OptionChoice(
			name = '中央本線(支線)',
			value = 'chuo-s'
		),
		OptionChoice(
			name = '中央本線(西)',
			value = 'chuo-w'
		),
		OptionChoice(
			name = '大糸線',
			value = 'oito'
		),
		OptionChoice(
			name = '飯田線',
			value = 'iida'
		)
	]
	STATUS_COLOR: dict[str, list[int]] = {
		'operational': [69, 240, 232],
		'restored':  [54, 169, 96],
		'delaying': [250, 221, 84],
		'others': [250, 68, 165],
		'information': [140, 140, 140]
	}

class TrainInfo(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[TrainInfo] Loading extension "TrainInfo"...')
		self.bot: Bot = bot
		log('[TrainInfo] Extension "TrainInfo" loaded.')
		return
	
	# Command: /traininfo <line>
	@command(
		name = 'traininfo',
		description = '運行状況を確認します [Extension: TrainInfo]'
	)
	@option(
		name = 'line',
		input_type = str,
		description = '路線を指定します',
		required = True,
		choices = TrainInfoData.LINE_CHOICES
	)
	async def __traininfo(self, ctx: ApplicationContext, line: str) -> None:
		data = get('%s/%s/%s' % (CONST_OTHERS.TRAININFO_DIAGRAM_INFO) + tuple(TrainInfoData.LINE_IDS[line]), headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
		data.encoding = 'utf-8'

		bs = BeautifulSoup(data.text, 'html.parser')

		icon = '<:line_warn:1246318701138022432> '
		match bs.select('#mdServiceStatus')[0].dt.text:
			case '平常運転':
				icon = '<:line_ok:1246318627305820282> '
				status = 'operational'
				status_text = bs.select('#mdServiceStatus')[0].dd.text
				status_datetime = dt.now().astimezone(tz=tz(offset=td(hours=9)))
				if '掲載' in bs.select('#mdServiceStatus')[0].dd.text:
					status = 'restored'
					text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
					status_text = text[0]
					status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
			case '運転状況':
				status = 'delaying'
				text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
				status_text = text[0]
				status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
			case 'その他':
				status = 'others'
				text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
				status_text = text[0]
				status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
			case '運転情報':
				status = 'information'
				text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
				status_text = text[0]
				status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
		
		embed = Embed(title='%s の運行情報' % [option.name for option in TrainInfoData.LINE_CHOICES if option.value == line][0], color=Color.from_rgb(TrainInfoData.STATUS_COLOR[status][0], TrainInfoData.STATUS_COLOR[status][1], TrainInfoData.STATUS_COLOR[status][2]))
		embed.description = '%s' % status_text
		embed.url = '%s/%s/%s' % (CONST_OTHERS.TRAININFO_DIAGRAM_INFO) + tuple(TrainInfoData.LINE_IDS[line])
		embed.add_field(name='運行状況', value=icon + bs.select('#mdServiceStatus')[0].dt.text, inline=True)
		embed.add_field(name='掲載日時', value=status_datetime.strftime(CONST_DATE.FORMAT.replace(':%S', '')), inline=True)
		embed.timestamp = dt.now()
		embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)
		embed.set_footer(text='%s@%s issued: /traininfo' % (ctx.author.display_name, ctx.author.name), icon_url=ctx.author.display_avatar.url)

		await ctx.respond(embed=embed)
		return

	# Command: /traininfo-local <area> <line>
	@command(
		name = 'traininfo-local',
		description = '運行状況を確認します [Extension: TrainInfo]'
	)
	@option(
		name = 'area',
		input_type = str,
		description = 'エリアを指定します',
		required = True,
		autocomplete = AutoComplete.getTrainInfoAreas
	)
	@option(
		name = 'line',
		input_type = str,
		description = '路線を指定します',
		required = True,
		autocomplete = AutoComplete.getTrainInfoLines
	)
	async def __traininfo_all(self, ctx: ApplicationContext, area: str, line: str) -> None:
		try:
			data = get('%s%s' % (CONST_OTHERS.TRAININFO_DOMAIN, line), headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
		except:
			await ctx.respond('Error: 指定された路線は存在しません！')
			return
		data.encoding = 'utf-8'

		bs = BeautifulSoup(data.text, 'html.parser')
		icon = '<:line_warn:1246318701138022432> '
		match bs.select('#mdServiceStatus')[0].dt.text:
			case '平常運転':
				icon = '<:line_ok:1246318627305820282> '
				status = 'operational'
				status_text = bs.select('#mdServiceStatus')[0].dd.text
				status_datetime = dt.now().astimezone(tz=tz(offset=td(hours=9)))
				if '掲載' in bs.select('#mdServiceStatus')[0].dd.text:
					status = 'restored'
					text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
					status_text = text[0]
					status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
			case '運転状況':
				status = 'delaying'
				text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
				status_text = text[0]
				status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
			case '列車遅延':
				status = 'delaying'
				text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
				status_text = text[0]
				status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
			case 'その他':
				status = 'others'
				text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
				status_text = text[0]
				status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
			case '運転情報':
				status = 'information'
				text = bs.select('#mdServiceStatus')[0].dd.text.split('（')
				status_text = text[0]
				status_datetime = dt.strptime(sub('(?<!\d)([0-9]{1})([月日時分])', '0\\1\\2', dt.now().strftime('%Y年') + text[1].replace('）', '')), '%Y年%m月%d日 %H時%M分掲載').astimezone(tz=tz(offset=td(hours=9)))
		
		embed = Embed(title='%s の運行情報' % bs.select('h1.title')[0].text, color=Color.from_rgb(TrainInfoData.STATUS_COLOR[status][0], TrainInfoData.STATUS_COLOR[status][1], TrainInfoData.STATUS_COLOR[status][2]))
		embed.set_author(
			name = CONST_OTHERS.BOT_NAME,
			icon_url = CONST_OTHERS.BOT_ICON_URL
		)
		embed.description = '%s' % status_text
		embed.url = '%s%s' % (CONST_OTHERS.TRAININFO_DOMAIN, line)
		embed.add_field(name='運行状況', value=icon + bs.select('#mdServiceStatus')[0].dt.text, inline=True)
		embed.add_field(name='掲載日時', value=status_datetime.strftime(CONST_DATE.FORMAT.replace(':%S', '')), inline=True)
		embed.timestamp = dt.now()
		embed.set_footer(text='%s@%s issued: /traininfo-all' % (ctx.author.display_name, ctx.author.name), icon_url=ctx.author.display_avatar.url)

		await ctx.respond(embed=embed)
		return

# ----------------------------

def setup(bot: Bot):
	bot.add_cog(TrainInfo(bot=bot))