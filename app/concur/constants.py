import re


DATABASE_URL = 'postgresql+psycopg2://postgres@localhost/concur'

SUCCESS = {'success': True}

RE_BEARER_AUTH_HEADER = re.compile(r'bearer ([a-zA-Z0-9]{50})', re.I)
