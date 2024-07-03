from .constants import CONST_DATE, CONST_LOG

from discord import ApplicationContext
from datetime import datetime as dt, timezone as tz, timedelta as td
from stringcolor import *
from random import choices
from datetime import timedelta as td
from string import digits, ascii_letters
from os import urandom
from hashlib import md5

def log(text: str, end: str = '\n', log_level: int = CONST_LOG.INFO) -> None:
	now = dt.now().astimezone(tz=tz(offset=td(hours=9)))

	match log_level:
		case CONST_LOG.DEBUG:
			log_type = cs(string='DEBUG', color='Grey4')
		case CONST_LOG.INFO:
			log_type = cs(string='INFO', color='SteelBlue')
		case CONST_LOG.WARN:
			log_type = cs(string='WARN', color='Yellow2')
		case CONST_LOG.ERROR:
			log_type = cs(string='ERROR', color='Red3')
		case _:
			log_type = cs(string='INFO', color='SteelBlue')

	print('[%s][%s] %s' % (now.strftime(format=CONST_DATE.FORMAT), log_type, text), end=end)
	return

def is_owner(ctx: ApplicationContext):
	return ctx.user == ctx.guild.owner

def randomString(len: int) -> str:
	return ''.join(choices(ascii_letters + digits, k=len))

def getHms(td: td):
	m, s = divmod(td.seconds, 60)
	h, m = divmod(m, 60)

	return h, m, s

def randomStringHex(length: int = 8):
	buf = ''
	while len(buf) < length:
		buf += md5(urandom(100)).hexdigest()
	return buf[0:length]