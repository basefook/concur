import sqlalchemy as sa
import passlib.context

from datetime import timedelta

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from concur.collections import enum

from .types import (
    INTEGER,
    BOOLEAN,
    PUBLIC_ID,
    VARCHAR,
    TSVECTOR,
    UTC_TIMESTAMP,
    OAUTH_TOKEN,
    UUID,
)


Base = declarative_base()


class Entity(object):
    id = sa.Column(PUBLIC_ID, primary_key=True)
    created_at = sa.Column(UTC_TIMESTAMP, nullable=False, index=True)
    deleted_at = sa.Column(UTC_TIMESTAMP, nullable=True)

    def __init__(self, *args, **kwargs):
        self.id = PUBLIC_ID.next_id()
        self.created_at = UTC_TIMESTAMP.now()


class User(Entity, Base):
    __tablename__ = 'users'

    _bcrypt = passlib.context.CryptContext(
        schemes=['bcrypt'],
        bcrypt__rounds=13,
        bcrypt__vary_rounds=0.1)

    email = sa.Column(VARCHAR, index=True, nullable=False)
    password = sa.Column(VARCHAR, nullable=False)
    group_id = sa.Column(UUID, index=True, nullable=False)

    def __init__(self, password, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        Entity.__init__(self)
        self.group_id = UUID.random()
        self.password = self._bcrypt.encrypt(password.encode('utf-8'))

    def __json__(self, request=None):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at,
        }

    def verify_password(self, password):
        """ Check that the password provided matches the encrypted password
            stored. Return True if verification succeeds.
        """
        if self.password is None:
            # TODO: log this
            return False
        ok, password = self._bcrypt.verify_and_update(
            password.encode('utf-8'), self.password)
        if not ok:
            return False
        if password:
            self.password = password
        return True


class Poll(Entity, Base):
    __tablename__ = 'polls'

    user_id = sa.Column(PUBLIC_ID, sa.ForeignKey(User.id), nullable=False)
    prompt = sa.Column(VARCHAR, nullable=False)
    prompt_tsv = sa.Column(TSVECTOR, nullable=False)

    creator = relationship(User)

    def __init__(self, creator, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        Entity.__init__(self)
        self.creator = creator
        self.prompt_tsv = sa.func.to_tsvector(self.prompt)


class Option(Entity, Base):
    __tablename__ = 'options'

    user_id = sa.Column(PUBLIC_ID, sa.ForeignKey(User.id), nullable=False)
    poll_id = sa.Column(PUBLIC_ID, sa.ForeignKey(Poll.id), index=True, nullable=False)
    text = sa.Column(VARCHAR, nullable=False)
    text_tsv = sa.Column(TSVECTOR, nullable=False)
    tally = sa.Column(INTEGER, default=0)
    likes = sa.Column(INTEGER, default=0)
    dislikes = sa.Column(INTEGER, default=0)

    creator = relationship(User)
    poll = relationship(Poll, backref='options')

    def __init__(self, creator, poll, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        Entity.__init__(self)
        self.text_tsv = sa.func.to_tsvector(self.text)
        self.poll = poll
        self.creator = creator


class Vote(Entity, Base):
    __tablename__ = 'votes'

    user_id = sa.Column(PUBLIC_ID, sa.ForeignKey(User.id), primary_key=True)
    option_id = sa.Column(PUBLIC_ID, primary_key=True)
    is_public = sa.Column(BOOLEAN, default=False)

    voter = relationship(User, backref='votes')

    def __init__(self, voter, *args, **kwargs):
        super(Vote, self).__init__(*args, **kwargs)
        self.voter = voter


class Grant(Entity, Base):
    __tablename__ = 'grants'

    TYPES = enum('PASSWORD')

    access_token = sa.Column(OAUTH_TOKEN, primary_key=True)
    refresh_token = sa.Column(OAUTH_TOKEN)
    grant_type = sa.Column(VARCHAR(16), nullable=False, index=True)
    user_id = sa.Column(PUBLIC_ID, sa.ForeignKey(User.id), index=True)
    expires_at = sa.Column(UTC_TIMESTAMP, nullable=False)
    user_agent = sa.Column(VARCHAR)
    ip_addr = sa.Column(VARCHAR)

    grantee = relationship(User, backref='grants')

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        Entity.__init__(self)
        self.access_token = OAUTH_TOKEN.next_token()

    def __json__(self, request=None):
        grant_json = {
            'type': self.grant_type
        }
        if self.grant_type == self.TYPES.PASSWORD:
            grant_json.update({
                'id': self.id,
                'access_token': self.access_token,
                'expires_at': self.expires_at,
            })
        return grant_json

    @classmethod
    def new_password_grant(cls, grantee, user_agent, ip_addr):
        grant = cls(grant_type=cls.TYPES.PASSWORD,
                    user_agent=user_agent,
                    ip_addr=ip_addr)
        grant.grantee = grantee
        grant.expires_at = grant.created_at + timedelta(days=60)
        return grant


class GroupMembership(Entity, Base):
    __tablename__ = 'users_2_groups'

    user_id = sa.Column(PUBLIC_ID, sa.ForeignKey(User.id), primary_key=True)
    group_id = sa.Column(UUID, primary_key=True)
    created_at = sa.Column(UTC_TIMESTAMP, default=UTC_TIMESTAMP.now, nullable=False, index=True)

    users = relationship(User, foreign_keys=[user_id], backref='groups')

    def __init__(self, user, group_id):
        Base.__init__(self)
        Entity.__init__(self)
        self.user_id = user.id
        self.group_id = group_id
