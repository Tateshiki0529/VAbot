from discord import (
	Cog, Bot, ApplicationContext, File, OptionChoice, Message, FFmpegPCMAudio
)
from discord import option
from discord.ext.commands import slash_command as command
from urllib.parse import urlencode
from requests import post
from io import BytesIO
from asyncio import sleep as asleep

from .constants import CONST_OTHERS
from .functions import log

class VOICEVOX(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[VOICEVOX] Loading module "VOICEVOX"...')
		self.bot: Bot = bot
		self.tts = False
		log('[VOICEVOX] Module "VOICEVOX" loaded.')

	"""OptionChoice(name='雀松朱司', value=52),
			OptionChoice(name='麒ヶ島宗麟', value=53),
			OptionChoice(name='春歌ナナ', value=54),
			OptionChoice(name='猫使アル', value=55),
			OptionChoice(name='猫使ビィ', value=58),"""
	@command(
		name = 'make-voice',
		description = '音声を合成します [Module: VOICEVOX]'
	)
	@option(
		name = 'text',
		type = str,
		description = '音声化するテキスト',
		required = True
	)
	@option(
		name = 'speaker',
		type = int,
		description = 'キャラクター番号',
		required = True,
		default = 3,
		choices = [
			OptionChoice(name='ずんだもん', value=3),
			OptionChoice(name='四国めたん', value=2),
			OptionChoice(name='春日部つむぎ', value=8),
			OptionChoice(name='雨晴はう', value=10),
			OptionChoice(name='波音リツ', value=9),

			OptionChoice(name='玄野武宏', value=11),
			OptionChoice(name='白上虎太郎', value=12),
			OptionChoice(name='青山龍星', value=13),
			OptionChoice(name='冥鳴ひまり', value=14),
			OptionChoice(name='九州そら', value=16),

			OptionChoice(name='もち子さん', value=20),
			OptionChoice(name='剣崎雌雄', value=21),
			OptionChoice(name='WhiteCUL', value=23),
			OptionChoice(name='後鬼', value=27),
			OptionChoice(name='No.7', value=29),

			OptionChoice(name='櫻歌ミコ', value=43),
			OptionChoice(name='ちび式じい', value=42),
			OptionChoice(name='小夜/SAYO', value=46),
			OptionChoice(name='ナースロボ＿タイプＴ', value=47),
			OptionChoice(name='†聖騎士 紅桜†', value=51),

			OptionChoice(name='中国うさぎ', value=61),
			OptionChoice(name='栗田まろん', value=67),
			OptionChoice(name='あいえるたん', value=68),
			OptionChoice(name='満別花丸', value=69),
			OptionChoice(name='琴詠ニア', value=74)
			
		]
	)
	
	async def __make_voice(self, ctx: ApplicationContext, text: str, speaker: int) -> None:
		await ctx.defer()
		audio = self.getAudio(text=text, speaker=speaker)
		if audio:
			await ctx.respond(file=File(fp=BytesIO(audio), filename='voice.wav'))
			return
		else:
			await ctx.respond(content='Error: ファイルの生成に失敗しました')
			return
		

	
	def getAudio(self, text: str, speaker: int) -> bytes | None:
		queryData = post('http://localhost:50021/audio_query?%s' % urlencode({
			'speaker': speaker,
			'text': text
		}))
		queryData.encoding = 'utf-8'

		audio = post('http://localhost:50021/synthesis?%s' % urlencode({
			'speaker': speaker,
			'pitchScale': 1.33,
			'speedScale': 1.2
		}), data=queryData, headers={'Content-Type': 'application/json'})

		if audio.status_code == 200:
			return audio.content
		else:
			return None
		
	@command(
		name = 'tts-vv',
		description = 'VOICEVOXによる読み上げを開始します [Module: VOICEVOX]'
	)
	@option(
		name = 'speaker',
		type = int,
		description = 'キャラクター番号',
		required = True,
		default = 3,
		choices = [
			OptionChoice(name='ずんだもん', value=3),
			OptionChoice(name='四国めたん', value=2),
			OptionChoice(name='春日部つむぎ', value=8),
			OptionChoice(name='雨晴はう', value=10),
			OptionChoice(name='波音リツ', value=9),

			OptionChoice(name='玄野武宏', value=11),
			OptionChoice(name='白上虎太郎', value=12),
			OptionChoice(name='青山龍星', value=13),
			OptionChoice(name='冥鳴ひまり', value=14),
			OptionChoice(name='九州そら', value=16),

			OptionChoice(name='もち子さん', value=20),
			OptionChoice(name='剣崎雌雄', value=21),
			OptionChoice(name='WhiteCUL', value=23),
			OptionChoice(name='後鬼', value=27),
			OptionChoice(name='No.7', value=29),

			OptionChoice(name='櫻歌ミコ', value=43),
			OptionChoice(name='ちび式じい', value=42),
			OptionChoice(name='小夜/SAYO', value=46),
			OptionChoice(name='ナースロボ＿タイプＴ', value=47),
			OptionChoice(name='†聖騎士 紅桜†', value=51),

			OptionChoice(name='中国うさぎ', value=61),
			OptionChoice(name='栗田まろん', value=67),
			OptionChoice(name='あいえるたん', value=68),
			OptionChoice(name='満別花丸', value=69),
			OptionChoice(name='琴詠ニア', value=74)
			
		]
	)
	async def __tts_vv(self, ctx: ApplicationContext, speaker: int) -> None:
		if not ctx.user.voice:
			await ctx.respond('Error: ボイスチャンネルに入ってから実行してください！')
			return
		else:
			self.vc = ctx.user.voice.channel
		
		self.voice = await self.vc.connect()
		self.tts = True
		self.tts_speaker = speaker
		await ctx.respond('ボイスチャンネル %s に接続しました！' % self.vc.mention)
		return
	
	@Cog.listener()
	async def on_message(self, msg: Message) -> None:
		if self.tts and self.voice and self.tts_speaker and not msg.author.bot:
			splitted = msg.content.splitlines()
			audios: list[bytes | None] = []
			'''for i in range(0, len(splitted)):
				if i == 0:
					audios.append(self.getAudio('%sさん %s' % (msg.author.display_name, splitted[i]), self.tts_speaker))
				else:
					audios.append(self.getAudio('%s' % splitted[i], self.tts_speaker))'''
			if self.voice.is_playing(): self.voice.stop()
			for i in range(0, len(splitted)):
				# audio = audios[i]
				if i == 0:
					audio = self.getAudio('%sさん %s' % (msg.author.display_name, splitted[i]), self.tts_speaker)
				else:
					audio = self.getAudio('%s' % splitted[i], self.tts_speaker)
				if audio: 
					with open('%s/voice.wav' % CONST_OTHERS.BOT_DIRECTORY, 'wb') as fp:
						fp.write(audio)
						self.voice.play(FFmpegPCMAudio('%s/voice.wav' % CONST_OTHERS.BOT_DIRECTORY))
						while self.voice.is_playing():
							await asleep(0.1)