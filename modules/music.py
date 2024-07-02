from discord import (
	Cog, Bot, ApplicationContext, Embed, Interaction, FFmpegPCMAudio, ActivityType, VoiceClient, Attachment
)
from discord import ClientException
from discord.activity import Activity
from discord import option
from discord.ext.commands import slash_command as command

import pycurl
from yt_dlp import YoutubeDL
from asyncio import sleep as asleep, run_coroutine_threadsafe, get_event_loop, run
from json import dump, load
from datetime import timedelta as td
from os.path import isfile
from io import BytesIO
from os import remove
from urllib.parse import urlparse, parse_qs

from .constants import CONST_OTHERS
from .functions import log

class Music(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Music] Loading module "Music"...')
		self.bot: Bot = bot
		self.repeat = None
		log('[Music] Module "Music" loaded.')
		return
	
	@command(
		name = 'set-cookie',
		description = '専用Cookieをセットします [Module: Music]'
	)
	@option(
		name = 'cookie_file',
		type = Attachment,
		description = 'Cookieのファイル',
		required = True
	)
	async def __set_cookie(self, ctx: ApplicationContext, cookie_file: Attachment) -> None:
		await ctx.defer()
		before_file = '%s/cookies/%s_before.txt' % (CONST_OTHERS.BOT_DIRECTORY, ctx.user.id)
		after_file = '%s/cookies/%s.txt' % (CONST_OTHERS.BOT_DIRECTORY, ctx.user.id)
		with open(before_file, 'wb') as fp:
			await cookie_file.save(fp)
		
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, 'https://www.youtube.com/')
		curl.setopt(pycurl.COOKIEFILE, before_file),
		curl.setopt(pycurl.COOKIEJAR, after_file)
		b = BytesIO()
		curl.setopt(pycurl.WRITEFUNCTION, b.write)

		curl.perform()

		if isfile(after_file): remove(before_file)
		await ctx.respond('Cookieファイルを保存しました！')
	
	@command(
		name = 'play',
		description = '音楽を再生します [Module: Music]'
	)
	@option(
		name = 'url',
		type = str,
		description = 'YouTubeのURL(短縮URLも可)',
		required = True
	)
	async def __play(self, ctx: ApplicationContext, url: str) -> None:
		if not ctx.user.voice:
			await ctx.respond('Error: ボイスチャンネルに入ってから実行してください！')
			return
		
		self.vc = ctx.user.voice.channel
		try:
			self.voice = await self.vc.connect()
		except ClientException:
			for client in self.bot.voice_clients:
				client: VoiceClient = client
				if client.guild == ctx.guild:
					self.voice = client
		self.embed = Embed(title='YouTube Player', color=0xff0000)
		self.embed.description = '動画をダウンロードしています…'
		self.embed.set_footer(text='%s#%s issued: /play' % (ctx.user.display_name, ctx.user.name), icon_url=ctx.user.avatar.url)
		self.embed.set_author(name=CONST_OTHERS.BOT_NAME, url=url, icon_url=CONST_OTHERS.BOT_ICON_URL)
		self.interaction: Interaction = await ctx.respond(embed=self.embed)
		await asleep(0.5)
		audio_data = self.___download_music(url=url, ctx=ctx)
		self.audio_data = audio_data
		await asleep(0.5)

		if audio_data['success']:
			self.embed.description = '再生中…'
			self.embed.add_field(name='タイトル', value=audio_data['raw']['title'], inline=False)
			self.embed.add_field(name='アップロードしたユーザー', value='%s (%s)' % (audio_data['raw']['channel'], audio_data['raw']['uploader_id']), inline=False)
			self.embed.add_field(name='再生回数', value='%s 回' % format((audio_data['raw']['view_count'] if audio_data['raw']['view_count'] else 0), ','), inline=True)
			self.embed.add_field(name='高評価数', value='%s 回' % format((audio_data['raw']['like_count'] if audio_data['raw']['like_count'] else 0), ','), inline=True)
			self.embed.add_field(name='コメント数', value='%s 件' % format((audio_data['raw']['comment_count'] if audio_data['raw']['comment_count'] else 0), ','), inline=True)
			self.embed.set_thumbnail(url=audio_data['raw']['thumbnail'])
			await self.interaction.edit(embed=self.embed)
			await self.bot.change_presence(activity=Activity(name='▶ %s' % audio_data['raw']['title'], type=ActivityType.playing))
			try:
				self.voice.play(FFmpegPCMAudio(audio_data['filepath']))
				while True:
					if self.voice.is_playing():
						await asleep(0.5)
					else:
						if self.voice.is_paused():
							await asleep(0.5)
						else:
							if not self.repeat:
								break
							else:
								self.voice.play(FFmpegPCMAudio(audio_data['filepath']))
			finally:
				await self.voice.disconnect()
				await self.bot.change_presence(activity=None)
		
		self.voice = None
		self.vc = None
		self.embed = None
		self.interaction = None
		return

	@command(
		name = 'pause',
		description = '一時停止 / 一時停止解除します [Module: Music]'
	)
	async def __pause(self, ctx: ApplicationContext):
		if not self.voice.is_connected():
			await ctx.respond('Error: まず接続してから実行してください！')
			return
		if not self.voice.is_playing() and not self.voice.is_paused():
			await ctx.respond('Error: 音楽が再生されていません！')
			return
		
		if not self.voice.is_paused():
			self.voice.pause()
			await ctx.respond(':pause_button:')
			await self.bot.change_presence(activity=Activity(name='⏸ %s' % self.audio_data['raw']['title'], type=ActivityType.playing))
			return
		else:
			self.voice.resume()
			await ctx.respond(':arrow_forward:')
			await self.bot.change_presence(activity=Activity(name='▶ %s' % self.audio_data['raw']['title'], type=ActivityType.playing))
			return
		
	@command(
		name = 'stop',
		description = '再生を停止します [Module: Music]'
	)
	async def __stop(self, ctx: ApplicationContext):
		if not self.voice.is_connected():
			await ctx.respond('Error: まず接続してから実行してください！')
			return
		if not self.voice.is_playing():
			await ctx.respond('Error: 音楽が再生されていません！')
			return
		
		self.voice.stop()
		await ctx.respond(':stop_button:')
		return

	@command(
		name = 'repeat',
		description = 'リピートモードを設定します [Module: Music]'
	)
	async def __stop(self, ctx: ApplicationContext, mode: str):
		if not self.voice.is_connected():
			await ctx.respond('Error: まず接続してから実行してください！')
			return
		if not self.voice.is_playing():
			await ctx.respond('Error: 音楽が再生されていません！')
			return
		
		match self.repeat:
			case None:
				self.repeat = 'once'
				await ctx.respond(':repeat_one:')
				return
			case 'once':
				self.repeat = None
				await ctx.respond(':no_entry_sign:')
				return

	def ___get_progress(self, status: dict) -> None:
		match status['status']:
			case 'downloading':
				self.embed.description = '動画をダウンロードしています… (%s %%)' % status['_percent_str']
				run_coroutine_threadsafe(self.interaction.edit(embed=self.embed), get_event_loop())
			case 'finished':
				self.embed.description = 'ダウンロード完了！ (100 %)'
				run_coroutine_threadsafe(self.interaction.edit(embed=self.embed), get_event_loop())

	
	def ___download_music(self, url: str, ctx: ApplicationContext, options: dict | None = None) -> dict:
		ydl_opts = {
			'format': 'bestaudio',
			'ignoreerrors': True,
			'postprocessors': [
				{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'wav'
				}
			],
			'progress_hooks': [self.___get_progress],
			'noprogress': True,
			'outtmpl': '%s/music/' % CONST_OTHERS.BOT_DIRECTORY + '%(id)s.%(ext)s'
		}
		if isfile('%s/cookies/%s.txt' % (CONST_OTHERS.BOT_DIRECTORY, ctx.user.id)): ydl_opts['cookiefile'] = '%s/cookies/%s.txt' % (CONST_OTHERS.BOT_DIRECTORY, ctx.user.id)
		if options: ydl_opts = ydl_opts + options

		with YoutubeDL(params=ydl_opts) as ydl:
			log(urlparse(url).query)
			if not isfile('%s/music/%s.wav' % (CONST_OTHERS.BOT_DIRECTORY, dict(parse_qs(urlparse(url).query))['v'])):
				data = ydl.extract_info(url=url, process=False)
				with open('%s/music/%s.json' % (CONST_OTHERS.BOT_DIRECTORY, data['id']), 'w') as fp:
					dump(data, fp)
				code = ydl.download(url_list=[url])
			else:
				code = 0
				with open('%s/music/%s.json' % (CONST_OTHERS.BOT_DIRECTORY, dict(parse_qs(urlparse(url).query))['v']), 'r') as fp:
					data = load(fp)

		if code == 0:
			return {
				'success': True,
				'filepath': '%s/music/%s.wav' % (CONST_OTHERS.BOT_DIRECTORY, data['id']),
				'raw': data
			}
		else:
			return {
				'success': False
			}