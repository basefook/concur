import re
import hashlib
import sqlalchemy as sa
import pytz
import base36

from os import urandom
from datetime import datetime
from uuid import UUID as _UUID
from dateutil.parser import parse as parse_datetime

from Crypto import Random as _Random


from sqlalchemy.dialects.postgresql import (  # NOQA
    VARCHAR,
    TEXT,
    INTEGER,
    BIGINT,
    SMALLINT,
    NUMERIC,
    FLOAT,
    REAL,
    BOOLEAN,
    TIMESTAMP,
    TIME,
    DATE,
    JSON,
    JSONB,
    ARRAY,
    ENUM,
    UUID as POSTGRES_UUID,
    TSVECTOR,
)

from geoalchemy2 import (  # NOQA
    Geometry as GEOMETRY,
    Geography as GEOGRAPHY
)


class UTC_TIMESTAMP(sa.types.TypeDecorator):

    impl = TIMESTAMP(timezone=True)

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime):
            value.replace(tzinfo=pytz.utc)
        elif isinstance(value, int):
            value = datetime.fromtimestamp(value, pytz.utc)
        elif isinstance(value, str):
            value = parse_datetime(value).replace(tzinfo=pytz.utc)
        elif value is None:
            return None
        else:
            raise ValueError('invalid UTC_TIMESTAMP value.')

        return value

    @staticmethod
    def now():
        return datetime.now(pytz.utc)


class PRIMARY_ID(sa.types.TypeDecorator):

    impl = BIGINT

    @classmethod
    def next_id(cls):
        return sa.text('util.next_id()')


class OAUTH_TOKEN(sa.types.TypeDecorator):
    impl = VARCHAR(length=50)

    RE_OAUTH_TOKEN= re.compile(r'[a-fA-F0-9]{50}')

    @staticmethod
    def next_token():
        token = base36.dumps(int(hashlib.sha256(urandom(32)).hexdigest(), 16))
        return token + '0' if len(token) == 49 else token


class UUID(sa.types.TypeDecorator):
    """ Custom UUID type that always returns hex representation without dashes.
    """
    impl = POSTGRES_UUID

    RE_INVALID_UUID_CHARS = re.compile(r'[^a-fA-F0-9]')

    def process_bind_param(self, value, dialect):
        if not value:
            return None
        if isinstance(value, UUID):
            return value.hex
        else:
            return self.RE_INVALID_UUID_CHARS.sub('', value)

    def process_result_value(self, value, dialects):
        return value.replace('-', '') if value else None

    @classmethod
    def random(cls, as_hex=True):
        """ Return a random UUID backed by a cryptographically strong PRNG.
        """
        # we set the attr lazily to circumvent a prefork issue
        # in the Crypto libraru.
        if not hasattr(cls, '_random'):
            setattr(cls, '_random', _Random.new())

        uuid = _UUID(bytes=cls._random.read(16))
        return uuid.hex if as_hex else uuid



class PUBLIC_ID(UUID):
    """ Custom UUID type that always returns hex representation without dashes.
    """

    @classmethod
    def next_id(cls):
        return cls.random()



# only export sqlalchemy column types
__all__ = [k for k in locals() if not k.startswith('_') and k.isupper()]
