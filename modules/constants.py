from dotenv import load_dotenv
from os import getenv

load_dotenv()

class CONST_LOG:
	INFO = 0
	WARN = 1
	ERROR = 2
	DEBUG = -1

class CONST_DATE:
	FORMAT = '%Y/%m/%d %H:%M:%S'
	TIME_FORMAT = '%H:%M'

class CONST_ENV:
	DISCORD_TOKEN = getenv('DISCORD_TOKEN')
	DEV_DISCORD_TOKEN = getenv('DEV_DISCORD_TOKEN')

	TWITTER_CLIENT_ID = getenv('TWITTER_CLIENT_ID')
	TWITTER_CLIENT_SECRET = getenv('TWITTER_CLIENT_SECRET')

	OPENAI_API_KEY = getenv('OPENAI_API_KEY')

	YAHOO_CLIENT_ID = getenv('YAHOO_CLIENT_ID')

	OPENWEATHERMAP_API_KEY = getenv('OPENWEATHERMAP_API_KEY')

	DMDSS_API_KEY = getenv('DMDSS_API_KEY')

class CONST_OTHERS:
	GUILD_ID = int(getenv('DEV_GUILD_ID'))
	TRAININFO_DOMAIN = getenv('TRAININFO_DOMAIN')
	TRAININFO_DIAGRAM_INFO = getenv('TRAININFO_DIAGRAM_INFO')
	BOT_NAME = getenv('BOT_NAME')
	BOT_ICON_URL = getenv('BOT_ICON_URL')
	FIVE_THOUSAND_TRILLION_IMAGE_GENERATOR_URL = getenv('FIVE_THOUSAND_TRILLION_IMAGE_GENERATOR_URL')
	YESNO_API_URL = getenv('YESNO_API_URL')
	APP_URL = getenv('APP_URL')
	WALICA_DIRECTORY = getenv('WALICA_DIRECTORY')
	TOKEN_DIRECTORY = getenv('TOKEN_DIRECTORY')
	WEB_APP_DIRECTORY = getenv('WEB_APP_DIRECTORY')

class CONST_WEATHER:
	API_URL = getenv('WEATHER_API_URL')
	API_KEY = getenv('WEATHER_API_KEY')
	WEATHER_ICON_URL = getenv('WEATHER_ICON_URL')
	UNIV_LAT = getenv('UNIV_LAT')
	UNIV_LNG = getenv('UNIV_LNG')