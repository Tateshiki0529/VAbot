from discord import AutocompleteContext, OptionChoice
from json import load
from glob import glob
from os.path import split as psplit

from .versions import VersionInfo
from .constants import CONST_OTHERS

class AutoComplete:
	async def loadImageAsync(self, ctx: AutocompleteContext) -> list:
		with open(file='./imagelist.json', mode='r') as fp:
			image_list = load(fp=fp)
		names = []
		for im in image_list:
			if ctx.value in im['image_name']:
				names.append(im['image_name'])
		
		return names
	
	async def getModules(self, ctx: AutocompleteContext) -> list[str]:
		return [e for e in ctx.bot.extensions.keys() if ctx.value in e]

	async def getVersion(self, ctx: AutocompleteContext) -> list[str]:
		return [ver for ver in list(VersionInfo.description.keys()) if ver.startswith(ctx.value)]
	
	async def getTrainInfoAreas(self, ctx: AutocompleteContext) -> list[str]:
		with open('./lines.json', 'r') as fp:
			json = load(fp=fp)
		areas = set([r[0] for r in json])
		return [area for area in areas if ctx.value in area]
	
	async def getTrainInfoLines(self, ctx: AutocompleteContext) -> list[OptionChoice]:
		with open('./lines.json', 'r') as fp: 
			json = load(fp=fp)
		lines = [r for r in json if r[0] == ctx.options['area']]
		return [OptionChoice(name=line[1], value=line[2]) for line in lines if ctx.value in line[1]]
	
	async def getWalicaEvent(self, ctx: AutocompleteContext) -> list[OptionChoice]:
		output: list[OptionChoice] = []
		for event in glob('%s/.events/*.json' % CONST_OTHERS.WALICA_DIRECTORY):
			with open(event, 'r') as fp:
				data = load(fp)
				if ctx.value in data['eventName']:
					output.append(OptionChoice(
						name = data['eventName'],
						value = data['eventId']
					))
		return output
	
	async def getWalicaItem(self, ctx: AutocompleteContext) -> list[OptionChoice]:
		output: list[OptionChoice] = []
		eventDataPath = '%s/.events/%s.json' % (CONST_OTHERS.WALICA_DIRECTORY, ctx.options['event_id'])
		with open(eventDataPath, 'r') as fp:
			eventData = load(fp)
			for v in eventData['eventCostDetails']:
				if ctx.value in v['itemName']:
					output.append(OptionChoice(
						name = v['itemName'],
						value = v['itemId']
					))
		return output