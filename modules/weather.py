from discord import (
	Cog, Bot, ApplicationContext, Interaction, Embed
)
from discord.ext.commands import slash_command as command
from discord.ext.tasks import loop
from asyncio import sleep as asleep
from datetime import timedelta as td, timezone as tz, datetime as dt
from datetime import time
from os.path import isfile
from os import remove
from json import load, loads
from requests import get
from urllib.parse import urlencode

from .functions import randomString, getHms, log
from .constants import CONST_WEATHER, CONST_OTHERS, CONST_DATE

class Weather(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Weather] Loading module \"Weather\"...')
		self.bot: Bot = bot
		self.task = self.__send_forecast.start()
		log('[Weather] Module \"Weather\" loaded.')
	
	def cog_unload(self) -> None:
		self.__send_forecast.cancel()

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
	
	@loop(
		time = [
			time(hour=6, tzinfo=tz(td(hours=9))),
			time(hour=21, tzinfo=tz(td(hours=9)))
		]
	)
	async def __send_forecast(self):
		now = dt.now(tz=tz(td(hours=9)))
		if time(hour=0) <= now.time() and time(hour=6) > now.time():
			mode = 'next'
		elif time(hour=6) <= now.time() and time(hour=19) > now.time():
			mode = 'current'
		else:
			mode = 'next'
		
		mode = 'next'

		match mode:
			case 'current':
				weather_data = loads(get('%s?%s' % (CONST_WEATHER.API_URL, urlencode({
					'appid': CONST_WEATHER.API_KEY,
					'lat': CONST_WEATHER.UNIV_LAT,
					'lon': CONST_WEATHER.UNIV_LNG,
					'lang': 'ja',
					'dt': int(now.timestamp())
				}))).text)['data'][0]
				title = '今日の天気'
			case 'next':
				next_day = now.replace(hour=9)
				next_day = next_day + td(days=1)
				weather_data = loads(get('%s?%s' % (CONST_WEATHER.API_URL, urlencode({
					'appid': CONST_WEATHER.API_KEY,
					'lat': CONST_WEATHER.UNIV_LAT,
					'lon': CONST_WEATHER.UNIV_LNG,
					'lang': 'ja',
					'dt': int(next_day.timestamp())
				}))).text)['data'][0]
				title = '明日の天気'
		embed = Embed(title=title, color=0xeb6e4b, timestamp=now)
		embed.add_field(name='日の出 / 日の入り', value='%s / %s' % (dt.fromtimestamp(weather_data['sunrise']).strftime(CONST_DATE.TIME_FORMAT), dt.fromtimestamp(weather_data['sunset']).strftime(CONST_DATE.TIME_FORMAT)), inline=True)
		embed.add_field(name='気温 / 体感気温', value='%.2f ℃ / %.2f ℃' % (weather_data['temp'] - 273.15, weather_data['feels_like'] - 273.15), inline=True)
		embed.add_field(name='気圧', value='%s hPa' % format(weather_data['pressure'], ','), inline=True)
		embed.add_field(name='湿度', value='%s %%' % weather_data['humidity'], inline=True)
		embed.set_author(name='@Weather API', icon_url='%s/%s@2x.png' % (CONST_WEATHER.WEATHER_ICON_URL, weather_data['weather'][0]['icon']))

		await self.bot.get_channel(1098053856681799800).send(embed=embed)