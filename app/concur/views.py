from concur.lib.view import View, view_config, view_defaults, json_body
from concur.renderer import json_renderer
from concur.db.models import User, Poll, Option, Vote
from concur.contexts import UserContext, PollContext, OptionContext
from concur.constants import SUCCESS
from concur import schemas


@view_defaults(route_name='users')
class UsersAPI(View):

    @view_config(request_method='POST')
    @json_body(schemas.User, role='creator')
    def signup(self):
        user = User(email=self.req.json['email'],
                    password=self.req.json['password'])
        self.db.add(user)
        return user


@view_defaults(route_name='users', context=UserContext)
class UserAPI(View):

    @view_config(request_method='GET')
    @json_body(schemas.User)
    def get_user(self):
        return self.ctx.user


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


@view_defaults(route_name='poll', context=PollContext)
class PollAPI(View):

    @view_config(request_method='GET')
    @json_body(schemas.Poll)
    def get_poll(self):
        return self.ctx.poll


@view_defaults(route_name='options', context=PollContext)
class OptionsAPI(View):

    @view_config(request_method='POST')
    @json_body(schemas.Option, role='creator')
    def add_option(self):
        creator = self.req.session.user
        option = Option(creator, self.ctx.poll, text=self.req.json['text'])
        self.db.add(option)
        return option


@view_defaults(route_name='option', context=OptionContext)
class OptionAPI(View):

    @view_config(request_method='DELETE')
    @json_body(schemas.Poll)
    def delete_option(self):
        self.ctx.option.is_deleted = True
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
        ('users',           '/users'),
        ('user',            '/users/{user_id:.+}'),
        ('polls',           '/polls'),
        ('poll',            '/polls/{poll_id:.+}'),
        ('options',         '/polls/{poll_id:.+}/options'),
        ('option',          '/polls/{poll_id:.+}/options/{option_id:.+}'),
        ('votes',           '/votes'),
        ('vote',            '/votes/{vote_id:.+}'),
    ]

    for name, pattern in routes:
        config.add_route(name, pattern)

    config.add_renderer('json', json_renderer())
