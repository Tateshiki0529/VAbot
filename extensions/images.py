from discord import (
	Cog, Bot, ApplicationContext, Attachment, File, AutocompleteContext
)
from discord import option
from discord.ext.commands import (
	slash_command as command
)
from json import load, dump
from uuid import uuid4
from mimetypes import guess_type
from datetime import datetime as dt, timezone as tz, timedelta as td
from emoji import emojize
from os import remove

from .functions import log
from .constants import CONST_DATE
from .autocomplete import AutoComplete

class Images(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Images] Loading extension "Images"...')
		self.bot: Bot = bot
		log('[Images] Extension "Images" loaded.')
		return

	@command(
		name = 'image-edit',
		description = '登録画像の操作を行います [Extension: Images]'
	)
	@option(
		name = 'mode',
		type = str,
		description = '操作モード',
		required = True,
		choices = [
			'add',
			'replace',
			'view',
			'rename',
			'delete'
		]
	)
	@option(
		name = 'image_name',
		type = str,
		description = '画像の登録名',
		required = True,
		autocomplete = AutoComplete.loadImageAsync
	)
	@option(
		name = 'new_image_name',
		type = str,
		description = '新しい画像の登録名',
		required = False
	)
	@option(
		name = 'image',
		type = Attachment,
		description = '登録・差し替えをする画像',
		required = False
	)
	async def __image_edit(self, ctx: ApplicationContext, mode: str, image_name: str, new_image_name: str = None, image: Attachment = None) -> None:
		image_list = self.___loadImage()
		match mode:
			case 'add':
				if not image:
					await ctx.respond('Error: 画像を指定してください！')
					return

				for im in image_list:
					if im['image_name'] == image_name:
						await ctx.respond('Error: 画像名 `%s` は既に登録されています！' % image_name)
						return
				is_image = self.___detectImage(image=image.filename)
				if not is_image[0]:
					await ctx.respond('Error: 画像ファイルはJPEG, PNG, GIF以外は登録できません！')
					return
				filename = '%s.%s' % (uuid4(), is_image[1])
				filepath = './images/%s' % filename
				with open(file=filepath, mode='wb') as fp:
					await image.save(fp=fp)
				if self.___addImage(name=image_name, image_path=filepath, image_author=ctx.user.id):
					await ctx.respond('画像 `%s` を登録しました！' % image_name)
					return
			case 'view':
				image_list = self.___loadImage()
				for im in image_list:
					if im['image_name'] == image_name:
						author = self.bot.get_user(im['image_author'])
						await ctx.respond('登録名: `%s`\n登録ユーザー: `%s@%s`\n登録日: `%s`' % (im['image_name'], author.display_name, author.name, dt.fromtimestamp(float(im['image_datetime'])).astimezone(tz=tz(offset=td(hours=9))).strftime(CONST_DATE.FORMAT)), file=File(fp=im['image_path']))
						return
				
				await ctx.respond('Error: 画像 `%s` は存在しません！' % image_name)
				return
			case 'replace':
				if not image:
					await ctx.respond('Error: 画像を指定してください！')
					return
				image_object = None
				for i in range(0, len(image_list)):
					if image_list[i]['image_name'] == image_name:
						image_object = image_list[i]
				
				if not image_object:
					await ctx.respond('Error: 画像 `%s` は存在しません！' % image_name)
					return
				if image_object['image_author'] != ctx.author.id:
					await ctx.respond('Error: 登録ユーザー以外は置き換えできません！')
					return
				is_image = self.___detectImage(image=image.filename)
				if not is_image[0]:
					await ctx.respond('Error: 画像ファイルはJPEG, PNG, GIF以外は登録できません！')
					return
				filename = '%s.%s' % (uuid4(), is_image[1])
				filepath = './images/%s' % filename
				with open(file=filepath, mode='wb') as fp:
					await image.save(fp=fp)
				for i in range(0, len(image_list)):
					if image_list[i]['image_name'] == image_name:
						remove(image_list[i]['image_path'])
						image_list[i]['image_path'] = filepath
						image_list[i]['image_datetime'] = int(dt.now().astimezone(tz=tz(offset=td(hours=9))).timestamp())
				self.___saveImage(list=image_list)
				await ctx.respond('画像 `%s` を置き換えしました！' % image_name)
				return
			case 'rename':
				if not new_image_name:
					await ctx.respond('Error: 新しい画像名を指定してください！')
					return
				image_object = None
				for i in range(0, len(image_list)):
					if image_list[i]['image_name'] == image_name:
						image_object = image_list[i]
				if not image_object:
					await ctx.respond('Error: 画像 `%s` は存在しません！' % image_name)
					return
				if image_object['image_author'] != ctx.author.id:
					await ctx.respond('Error: 登録ユーザー以外は名前の変更ができません！')
					return
				for i in range(0, len(image_list)):
					if image_list[i]['image_name'] == image_name:
						image_list[i]['image_name'] = new_image_name
				self.___saveImage(list=image_list)
				await ctx.respond('画像 `%s` の名前を `%s` に変更しました！' % (image_name, new_image_name))
				return
			case 'delete':
				image_object = None
				for i in range(0, len(image_list)):
					if image_list[i]['image_name'] == image_name:
						image_object = image_list[i]
				if not image_object:
					await ctx.respond('Error: 画像 `%s` は存在しません！' % image_name)
					return
				if image_object['image_author'] != ctx.author.id:
					await ctx.respond('Error: 登録ユーザー以外は削除ができません！')
					return
				for i in range(0, len(image_list)):
					if image_list[i]['image_name'] == image_name:
						image_list.pop(i)
						remove(image_object['image_path'])
				self.___saveImage(list=image_list)
				await ctx.respond('画像 `%s` を削除しました！' % image_name)
				return
				
	# Command /im <image_name>
	@command(
		name = 'im',
		description = '画像を貼ります [Extension: Images]'
	)
	@option(
		name = 'image_name',
		type = str,
		description = '登録された画像名',
		autocomplete = AutoComplete.loadImageAsync
	)
	async def __im(self, ctx: ApplicationContext, image_name: str) -> None:
		image_list = self.___loadImage()
		for im in image_list:
			if im['image_name'] == image_name:
				author = self.bot.get_user(im['image_author'])
				await ctx.respond(emojize(':thumbsup:'), ephemeral=True, delete_after=3.0)
				await ctx.channel.send(file=File(fp=im['image_path']))
				return
		
		await ctx.respond('Error: 画像 `%s` は存在しません！' % image_name, ephemeral=True)
		return

	# --------------------------------

	def ___loadImage(self) -> list[dict]:
		with open(file='./imagelist.json', mode='r') as fp:
			return load(fp=fp)
	def ___saveImage(self, list: list[dict]) -> None:
		with open(file='./imagelist.json', mode='w') as fp:
			return dump(obj=list, fp=fp, indent=4)
	
	def ___addImage(self, name: str, image_path: str, image_author: int) -> bool:
		imageList: list[dict] = self.___loadImage()
		imageList.append({
			'image_name': name,
			'image_path': image_path,
			'image_datetime': int(dt.now().astimezone(tz=tz(offset=td(hours=9))).timestamp()),
			'image_author': image_author
		})
		self.___saveImage(list=imageList)

		return self.___loadImage() == imageList
	
	def ___detectImage(self, image: str) -> tuple[bool, str|None]:
		match guess_type(url=image)[0]:
			case 'image/png':
				return (True, 'png')
			case 'image/jpeg':
				return (True, 'jpg')
			case 'image/gif':
				return (True, 'gif')
			case _:
				return (False, None)

# ----------------------------

def setup(bot: Bot):
	bot.add_cog(Images(bot=bot))