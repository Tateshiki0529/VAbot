from discord import (
	Cog, Bot, ApplicationContext, Interaction
)
from discord.ext.commands import slash_command as command
from asyncio import sleep as asleep
from datetime import timedelta as td
from os.path import isfile
from os import remove
from json import load

from .functions import randomString, getHms, log
from .constants import CONST_WEATHER, CONST_OTHERS

class Weather(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Weather] Loading module \"Weather\"...')
		self.bot: Bot = bot
		log('[Weather] Module \"Weather\" loaded.')

	@command(
		name = 'get-location',
		description = '現在地を取得します [Module: Weather]'
	)
	async def __get_location(self, ctx: ApplicationContext) -> None:
		token = randomString(64)
		formatString = '以下のページで位置情報取得を行ってください:\n\nStatus: `{}`\n\nURL: {}'
		url = '%s/location.php?token=%s' % (CONST_OTHERS.APP_URL, token)
		status = '取得待ち'
		msg: Interaction = await ctx.respond(formatString.format(status, url), ephemeral=False)

		for i in range(0, 60):
			await asleep(5.0)
			remaining = td(seconds=(300 - ((i + 1) * 5)))
			h, m, s = getHms(remaining)
			status = '取得待ち (残り時間: 約%d分%d秒)' % (m, s)
			await msg.edit_original_response(content=formatString.format(status, url))
			if isfile('%s/%s.json' % (CONST_OTHERS.TOKEN_DIRECTORY, token)):
				with open('%s/%s.json' % (CONST_OTHERS.TOKEN_DIRECTORY, token)) as fp:
					json = load(fp=fp)
					
				remove('%s/%s.json' % (CONST_OTHERS.TOKEN_DIRECTORY, token))

				lat, lng = (json[0], json[1])
				status = '取得完了'
				await msg.edit_original_response(content=formatString.format(status, '(Completed)'))

				await asleep(5.0)

				await msg.edit_original_response(content='緯度: %s, 経度: %s' % (lat, lng))
				return

		status = '有効期限切れ'
		await msg.edit_original_response(content=formatString.format(status, '(Expired)'))
		return