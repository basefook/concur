import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from concur.collections import enum

from .types import (
    INTEGER,
    BOOLEAN,
    PUBLIC_ID,
    TEXT,
    TSVECTOR,
    UTC_TIMESTAMP,
    OAUTH_TOKEN,
)


Base = declarative_base()


class Entity(object):
    id = sa.Column(PUBLIC_ID, primary_key=True)
    created_at = sa.Column(UTC_TIMESTAMP, nullable=False, index=True)
    deleted_at = sa.Column(UTC_TIMESTAMP, nullable=True)

    def __init__(self, *args, **kwargs):
        self.id = PUBLIC_ID.next_id()
        self.created_at = UTC_TIMESTAMP.now()


class User(Base, Entity):
    __tablename__ = 'users'

    email = sa.Column(TEXT, index=True, nullable=False)
    password = sa.Column(TEXT, nullable=False)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)


class Poll(Base, Entity):
    __tablename__ = 'polls'

    user_id = sa.Column(PUBLIC_ID, nullable=False)
    prompt = sa.Column(TEXT, nullable=False)
    prompt_tsv = sa.Column(TSVECTOR, nullable=False)

    creator = relationship(User, backref='polls')

    def __init__(self, creator, *args, **kwargs):
        super(Poll, self).__init__(*args, **kwargs)
        self.creator = creator
        self.prompt_tsv = sa.func.to_tsvector(self.prompt)


class Option(Base, Entity):
    __tablename__ = 'options'

    user_id = sa.Column(PUBLIC_ID, sa.ForeignKey(User.id), nullable=False)
    poll_id = sa.Column(PUBLIC_ID, sa.ForeignKey(Poll.id), index=True, nullable=False)
    text = sa.Column(TEXT, nullable=False)
    text_tsv = sa.Column(TSVECTOR, nullable=False)
    tally = sa.Column(INTEGER, default=0)
    likes = sa.Column(INTEGER, default=0)
    dislikes = sa.Column(INTEGER, default=0)

    creator = relationship(User)
    poll = relationship(Poll, backref='options')

    def __init__(self, creator, poll, *args, **kwargs):
        super(Option, self).__init__(*args, **kwargs)
        self.text_tsv = sa.func.to_tsvector(self.text)
        self.poll = poll
        self.creator = creator


class Vote(Base, Entity):
    __tablename__ = 'votes'

    user_id = sa.Column(PUBLIC_ID, sa.ForeignKey(User.id), primary_key=True)
    option_id = sa.Column(PUBLIC_ID, primary_key=True)
    is_public = sa.Column(BOOLEAN, default=False)

    voter = relationship(User, backref='votes')

    def __init__(self, voter, *args, **kwargs):
        super(Vote, self).__init__(*args, **kwargs)
        self.voter = voter


class Grant(Base):
    __tablename__ = 'grants'

    TYPES = enum('PASSWORD')

    access_token = sa.Column(OAUTH_TOKEN, primary_key=True)
    refresh_token = sa.Column(OAUTH_TOKEN)
    grant_type = sa.Column(TEXT(16), nullable=False, index=True)
    user_id = sa.Column(PUBLIC_ID, ForeignKey(User.id), index=True)
    expires_at = sa.Column(UTC_TIMESTAMP, nullable=False)
    user_agent = sa.Column(TEXT)
    ip_addr = sa.Column(TEXT)

    @classmethod
    def new_password_grant(cls, user_public_id, user_agent, ip_addr):
        grant = cls(grant_type=cls.TYPES.PASSWORD,
                    user_public_id=user_public_id,
                    user_agent=user_agent,
                    ip_addr=ip_addr)
        grant.expires_at = grant.created_at + timedelta(days=60)
        return grant

