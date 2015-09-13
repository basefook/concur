from concur.lib.view import View, view_config, view_defaults, json_body
from concur.renderer import json_renderer
from concur.contexts import UserContext, PollContext, OptionContext, GrantContext
from concur.db.models import User, GroupMembership, Poll, Option, Vote, Grant
from concur.db.types import UTC_TIMESTAMP
from concur.constants import SUCCESS
from concur import schemas


@view_defaults(route_name='grants')
class GrantsAPI(View):

    @view_config(request_method='POST')
    def login(self):
        if self.req.json['type'].upper() == Grant.TYPES.PASSWORD:
            return self.login_with_password_grant()

    def login_with_password_grant(self):
        user = self.db.query(User)\
            .filter_by(email=self.req.json['email'])\
            .first()
        if not user:
            raise Exception('user not found')
        if not user.verify_password(self.req.json['password']):
            raise Exception('invalid email or password')
        self.req.session.remember(user)
        return self.req.session.grant


@view_defaults(route_name='grant')
class GrantAPI(View):

    @view_config(request_method='DELETE')
    def logout(self):
        self.ctx.grant.deleted_at = UTC_TIMESTAMP.now()
        return SUCCESS


@view_defaults(route_name='users')
class UsersAPI(View):

    @view_config(request_method='POST')
    @json_body(schemas.User, role='creator')
    def signup(self):
        user = User(email=self.req.json['email'],
                    password=self.req.json['password'])
        # users belong to their own group.
        group_membership = GroupMembership(user, group_id=user.group_id)
        self.db.add(user)
        self.db.add(group_membership)
        return user


@view_defaults(route_name='user')
class UserAPI(View):

    @view_config(request_method='GET')
    def get_user(self):
        return self.ctx.user

    @view_config(request_method='DELETE')
    def delete_user(self):
        self.ctx.user.deleted_at = UTC_TIMESTAMP.now()
        return SUCCESS


@view_defaults(route_name='polls')
class PollsAPI(View):

    @view_config(request_method='POST')
    @json_body(schemas.Poll, role='creator')
    def create_poll(self):
        creator = self.req.session.user
        poll = Poll(creator, prompt=self.req.json['prompt'])
        options = []
        for o in self.req.json['options']:
            options.append(Option(creator, poll, text=o['text']))
        self.db.add(poll)
        self.db.add_all(options)
        return poll


@view_defaults(route_name='poll')
class PollAPI(View):

    @view_config(request_method='GET')
    @json_body(schemas.Poll)
    def get_poll(self):
        return self.ctx.poll


@view_defaults(route_name='options')
class OptionsAPI(View):

    @view_config(request_method='POST')
    @json_body(schemas.Option, role='creator')
    def add_option(self):
        creator = self.req.session.user
        option = Option(creator, self.ctx.poll, text=self.req.json['text'])
        self.db.add(option)
        return option


@view_defaults(route_name='option')
class OptionAPI(View):

    @view_config(request_method='DELETE')
    @json_body(schemas.Poll)
    def delete_option(self):
        self.ctx.option.deleted_at = UTC_TIMESTAMP.now()
        return SUCCESS


@view_defaults(route_name='votes')
class VotesAPI(View):

    @view_config(request_method='POST')
    @json_body(schemas.Vote, role='creator')
    def cast_vote(self):
        option_id = self.req.matchdict['option_id']
        old_vote = self.db.query(Vote)\
            .filter(Vote.user_id == self.req.session.user.id,
                    Vote.option_id == option_id)\
            .first()
        if (not old_vote) or (old_vote.option_id != option_id):
            new_vote = Vote(self.req.session.user,
                            option_id=option_id)
            self.db.add(new_vote)
            return new_vote
        else:
            return old_vote


@view_defaults(route_name='vote')
class VoteAPI(View):
    pass


def includeme(config):
    routes = [
        ('grants', '/grants', None),
        ('grant', '/grants/{grant_id:.+}', GrantContext),
        ('users', '/users', None),
        ('user', '/users/{user_id:.+}', UserContext),
        ('polls', '/polls', None),
        ('poll', '/polls/{poll_id:.+}', PollContext),
        ('options', '/polls/{poll_id:.+}/options', None),
        ('option', '/polls/{poll_id:.+}/options/{option_id:.+}', OptionContext),
        ('votes', '/votes', None),
        ('vote', '/votes/{vote_id:.+}', None),
    ]

    for name, pattern, root_factory in routes:
        config.add_route(name, pattern, factory=root_factory)

    config.add_renderer('json', json_renderer())
