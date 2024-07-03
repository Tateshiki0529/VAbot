from discord import (
	Cog, Bot, ApplicationContext, Message, Interaction, HTTPException
)
from discord import option
from discord.ext.commands import slash_command as command
from emoji import emojize
from asyncio import create_subprocess_exec
from subprocess import PIPE, STDOUT
from json import loads, dumps

from .functions import log, CONST_LOG

class Gomamayo(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Gomamayo] Loading extension "Gomamayo"...')
		self.bot: Bot = bot
		log('[Gomamayo] Extension "Gomamayo" loaded.')
		return
	
	@Cog.listener()
	async def on_message(self, msg: Message) -> None:
			output = await self.___detectGomamayo(msg.content, dictionary='ipa')
			if output['isGomamayo']:
				try:
					p_message = msg.channel.get_partial_message(msg.id)
					await p_message.add_reaction(emoji='⁉')
					match output['detail'][0]['dimension']:
						case 1:
							await p_message.add_reaction(emoji='1⃣')
						case 2:
							await p_message.add_reaction(emoji='2⃣')
						case 3:
							await p_message.add_reaction(emoji='3⃣')
						case 4:
							await p_message.add_reaction(emoji='4⃣')
				except HTTPException as e:
					log(text=e.response, log_level=CONST_LOG.ERROR)
			return

	# Command: /gomamayo-debug <text>
	@command(
		name = 'gomamayo-debug',
		description = 'ゴママヨを判定します [Extension: Gomamayo]'
	)
	@option(
		name = 'text',
		type = str,
		description = 'ゴママヨ判定テキスト',
		required = True
	)
	@option(
		name = 'dict',
		type = str,
		description = '使用する辞書',
		required = False,
		default = 'ipa',
		choices = [
			'ipa',
			'neo',
			'uni',
			'uni3'
		]
	)
	async def __gomamayo_debug(self, ctx: ApplicationContext, text: str, dict: str = 'ipa') -> None:
		await ctx.defer()
		output = await self.___detectGomamayo(text, dictionary=dict)
		if output['isGomamayo']:
			output_d = dumps(output, indent=4, ensure_ascii=False)
			outputs = ['```\n' + output_d[i:i + 1900] + '\n```' for i in range(0, len(output_d), 1900)]
			await ctx.respond(emojize(':interrobang:') * output['detail'][0]['dimension'])
			for m in outputs:
				await ctx.channel.send(m)
		else:
			await ctx.respond('NOT GOMAMAYO')
		return

	# Command: /gomamayo <text>
	@command(
		name = 'gomamayo',
		description = 'ゴママヨを判定します [Extension: Gomamayo]'
	)
	@option(
		name = 'text',
		type = str,
		description = 'ゴママヨ判定テキスト',
		required = True
	)
	@option(
		name = 'dict',
		type = str,
		description = '使用する辞書',
		required = False,
		default = 'ipa',
		choices = [
			'ipa',
			'neo',
			'uni',
			'uni3'
		]
	)
	async def __gomamayo(self, ctx: ApplicationContext, text: str, dict: str = 'ipa') -> None:
		await ctx.defer()
		output = await self.___detectGomamayo(text, dictionary=dict)
		if output['isGomamayo']:
			await ctx.respond('%s' % text + emojize(':interrobang:') * output['detail'][0]['dimension'])
		else:
			await ctx.respond('NOT GOMAMAYO')
		return
	
	# ----------------------------------

	async def ___detectGomamayo(self, text: str, dictionary: str = 'ipa') -> dict:
		command = ['/usr/local/go/bin/gomamayo', 'analyze', '-sysdict', dictionary, text]
		result = await create_subprocess_exec(
			*command,
			stdout = PIPE,
			stderr = STDOUT
		)

		output, _ = await result.communicate()

		return loads(output)

# ----------------------------

def setup(bot: Bot):
	bot.add_cog(Gomamayo(bot=bot))