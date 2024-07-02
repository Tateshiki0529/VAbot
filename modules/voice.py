from discord import (
	Cog, Bot, ApplicationContext, Member, VoiceState, CategoryChannel, PermissionOverwrite, Role, Embed, TextChannel, Message
)
from discord import option, Color
from discord.ext.commands import slash_command as command
from typing import Union
from datetime import datetime as dt, timezone as tz, timedelta as td
from uuid import uuid4
import asyncio
from .functions import log, randomStringHex
from .constants import CONST_LOG, CONST_DATE, CONST_OTHERS



class Voice(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Voice] Loading module "Voice"...')
		self.bot: Bot = bot
		self.channels: list[dict[str, any]] = []
		log('[Voice] Module "Voice" loaded.')
		return

	async def ___delete_channel(self, ch: TextChannel, chObj: dict[str, any]) -> None:
		filename = str(uuid4())
		with open('%s/call-channel-history/%s.log' % (CONST_OTHERS.WEB_APP_DIRECTORY, filename), 'w') as fp:
			fp.write('- History Details -\nChannelName: %s (%s)\nUsers: %s\nCreatedAt: %s\n\n- Chat History -\n' % (ch.name, ch.id, ', '.join(['%s#%s' % (u.display_name, u.name) for u in ch.members if not u.bot]), chObj['createdAt'].strftime(CONST_DATE.FORMAT)) + '\n'.join(chObj['messages']))
		for user in ch.members:
			if not user.bot: await user.send(content='- チャットログ -\nチャンネル名: \#%s\nダウンロードURL: %s' % (ch.name, '%s/call-channel-history/%s.log' % (CONST_OTHERS.APP_URL, filename)))

		await ch.delete(reason='Channel closed')
		return

	@Cog.listener()
	async def on_message(self, msg: Message) -> None:
		for i in range(0, len(self.channels)):
			if msg.channel == self.channels[i]['channel']:
				if not msg.author.bot: self.channels[i]['messages'].append('[%s] %s#%s: %s' % (dt.now().astimezone(tz(td(hours=9))).strftime(CONST_DATE.FORMAT), msg.author.display_name, msg.author.name, msg.content))

	@command(
		name = 'call-channel',
		description = '通話用チャンネルを管理します [Module: Voice]'
	)
	@option(
		name = 'mode',
		type = str,
		description = 'コマンドのモード',
		choices = [
			'create',
			'remove',
			'add'
		],
		required = True
	)
	async def __call_channel(self, ctx: ApplicationContext, mode: str) -> None:
		match mode:
			case 'create':
				if not ctx.user.voice:
					await ctx.respond('Error: ボイスチャンネルに参加してから実行してください！')
					return
				channelId: str = randomStringHex(8)
				channelName: str = 'call-channel_%s' % channelId
				category: CategoryChannel = ctx.user.voice.channel.category
				overwrites: dict[Union[Role, Member], PermissionOverwrite] = {
						ctx.user.guild.default_role: PermissionOverwrite(
							view_channel = False,
							read_messages = False,
							send_messages = False
						)
					}
				for user in ctx.user.voice.channel.members:
					overwrites[user] = PermissionOverwrite(
						view_channel = True,
						read_messages = True,
						send_messages = True
					)
				callChannel = await ctx.user.guild.create_text_channel(
					name = channelName,
					reason = '%s#%s issued `/call-channel create` command' % (ctx.user.display_name, ctx.user.name),
					category = category,
					position = len(category.channels),
					overwrites = overwrites
				)
				embed = Embed(title='通話専用チャンネル#%s' % channelId, color=Color.random(), timestamp=dt.now())
				embed.description = '通話専用チャンネルを作成しました！'
				embed.add_field(name='チャンネル', value='%s' % callChannel.mention, inline=True)
				embed.add_field(name='対象のボイスチャンネル', value='%s' % ctx.user.voice.channel.mention, inline=True)
				embed.add_field(name='閲覧可能ユーザー', value=' '.join([u.mention for u in ctx.user.voice.channel.members]), inline=True)
				embed.add_field(name='作成日時', value=dt.now().astimezone(tz(td(hours=9))).strftime(CONST_DATE.FORMAT), inline=True)
				embed.set_author(
					name = CONST_OTHERS.BOT_NAME,
					icon_url = CONST_OTHERS.BOT_ICON_URL
				)
				embed.set_footer(text='%s#%s issued: /call-channel create' % (ctx.user.display_name, ctx.user.name), icon_url=ctx.user.avatar.url)
				firstMessage: Message = await callChannel.send(content='@here', embed=embed)
				self.channels.append({
					'name': callChannel.name,
					'id': callChannel.id,
					'channel': callChannel,
					'firstMessage': firstMessage,
					'firstMessageEmbed': embed, 
					'voiceChannel': ctx.user.voice.channel,
					'createdAt': dt.now().astimezone(tz(td(hours=9))),
					'users': [u for u in callChannel.members if not u.bot],
					'messages': []
				})
				await firstMessage.pin()
				await ctx.respond('チャンネルを作成しました! %s' % callChannel.mention, ephemeral=True)
				return
			case 'remove':
				if not ctx.user.voice:
					await ctx.respond('Error: ボイスチャンネルに参加してから実行してください！')
					return
				for channel in self.channels:
					if channel['voiceChannel'].id == ctx.user.voice.channel.id:
						await self.___delete_channel(ch=channel['channel'], chObj=channel)
						await ctx.respond('チャンネルを削除し、DMへログを送付しました！', ephemeral=True)
						return
				await ctx.respond('削除するチャンネルがありません！', ephemeral=True)
				return
			case 'refresh':
				pass
	
	@Cog.listener()
	async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
		if not after.channel:
			for i in range(0, len(self.channels)):
				if member in self.channels[i]['users']:
					self.channels[i]['users'] = [u for u in self.channels[i]['users'] if u != member]
					await self.channels[i]['channel'].set_permissions(target=member, overwrite=PermissionOverwrite(
						view_channel = False,
						read_messages = False,
						send_messages = False
					), reason='%s#%s left voice channel %s' % (member.display_name, member.name, self.channels[i]['voiceChannel'].name))
					embed: Embed = self.channels[i]['firstMessageEmbed']
					embed.set_field_at(index=2, name='閲覧可能ユーザー', value=' '.join([u.mention for u in self.channels[i]['voiceChannel'].members]))
					await self.channels[i]['firstMessage'].edit(embed=embed)
		else:
			for i in range(0, len(self.channels)):
				if member in self.channels[i]['users']:
					self.channels[i]['users'] = [u for u in self.channels[i]['users'] if u != member]
					await self.channels[i]['channel'].set_permissions(target=member, overwrite=PermissionOverwrite(
						view_channel = False,
						read_messages = False,
						send_messages = False
					), reason='%s#%s left voice channel %s' % (member.display_name, member.name, self.channels[i]['voiceChannel'].name))
					embed: Embed = self.channels[i]['firstMessageEmbed']
					embed.set_field_at(index=2, name='閲覧可能ユーザー', value=' '.join([u.mention for u in self.channels[i]['voiceChannel'].members]))
					await self.channels[i]['firstMessage'].edit(embed=embed)
			for i in range(0, len(self.channels)):
				if after.channel.name == self.channels[i]['voiceChannel'].name:
					self.channels[i]['users'].append(member)
					await self.channels[i]['channel'].set_permissions(target=member, overwrite=PermissionOverwrite(
						view_channel = True,
						read_messages = True,
						send_messages = True
					), reason='%s#%s joined voice channel %s' % (member.display_name, member.name, self.channels[i]['voiceChannel'].name))
					embed: Embed = self.channels[i]['firstMessageEmbed']
					embed.set_field_at(index=2, name='閲覧可能ユーザー', value=' '.join([u.mention for u in self.channels[i]['voiceChannel'].members]))
					await self.channels[i]['firstMessage'].edit(embed=embed)

		# log('[Voice] State changed (VoiceChannel#%s @ %s): %s -> %s' % ((member.voice.channel.name if member.voice else '---'), member.display_name, (before.channel.name if before.channel else 'None'), (after.channel.name if after.channel else 'None')), log_level=CONST_LOG.DEBUG)
		return