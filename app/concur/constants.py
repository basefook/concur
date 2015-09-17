import re

from concur.collections import enum


DATABASE_URL = 'postgresql+psycopg2://http:foo@localhost/concur'

SUCCESS = {'success': True}

RE_BEARER_AUTH_HEADER = re.compile(r'bearer ([a-zA-Z0-9]{50})', re.I)

ROLES = enum('CREATOR')
