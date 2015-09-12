import sqlalchemy as sa

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .types import (
    INTEGER,
    BOOLEAN,
    PUBLIC_ID,
    TEXT,
    TSVECTOR,
    UTC_TIMESTAMP,
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
