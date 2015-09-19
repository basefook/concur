import sqlalchemy as sa

from concur import schemas
from concur.db.models import (
    User, GroupMembership, Poll, Option,
    Vote, Grant, KeyCounter,
)

from concur.db.types import UTC_TIMESTAMP
from concur.auth.constants import PERMISSIONS
from concur.constants import ROLES, SUCCESS

from .lib.view import View, api_config, api_defaults, json_body
from . import exceptions as exc


@api_config(context=exc.ApiException)
def on_api_exception(exc_resp, request):
    """ This is what happens when we raise an API exception. ApiExceptions are
        themselves Response objects.
    """
    return exc_resp


# ------------------------------------------------------------------------------
@api_defaults(route_name='grants')
class GrantsAPI(View):

    @api_config(request_method='POST', login_required=False)
    def login(self):
        grant_type = self.req.json['type'].upper()
        if grant_type == Grant.TYPES.PASSWORD:
            return self.login_with_password_grant()

    def login_with_password_grant(self):
        if not self.ctx.grantee.verify_password(self.req.json['password']):
            raise exc.Unauthorized('invalid email or password')
        self.req.session.remember(self.ctx.grantee)
        return self.req.session.grant


@api_defaults(route_name='grant')
class GrantAPI(View):

    @api_config(request_method='DELETE', permission=PERMISSIONS.DELETE)
    def logout(self):
        self.ctx.grant.deleted_at = UTC_TIMESTAMP.now()
        return SUCCESS


# ------------------------------------------------------------------------------
@api_defaults(route_name='users')
class UsersAPI(View):

    @api_config(request_method='POST', login_required=False)
    @json_body(schemas.User, role=ROLES.CREATOR)
    def signup(self):
        if self.ctx.user is not None:
            raise exc.Conflict('email already registered')

        user = User(email=self.req.json['email'],
                    password=self.req.json['password'])

        # users belong to their own group.
        group_membership = GroupMembership(user, group_id=user.group_id)

        self.db.add(user)
        self.db.add(group_membership)
        return user


@api_defaults(route_name='user')
class UserAPI(View):

    @api_config(request_method='GET', permission=PERMISSIONS.READ)
    def get_user(self):
        return self.ctx.user

    @api_config(request_method='DELETE', permission=PERMISSIONS.DELETE)
    def delete_user(self):
        self.ctx.user.deleted_at = UTC_TIMESTAMP.now()
        return SUCCESS

    @api_config(route_name='verify_user', request_method='GET',
                 login_required=False)
    def verify_user(self):
        user = self.ctx.user
        if not user or user.is_verified:
            raise exc.Unauthorized()
        code = self.req.GET.get('code')
        if not (code and (user.verification_code == code)):
            raise exc.Unauthorized()
        else:
            user.is_verified = True
            return SUCCESS

# ------------------------------------------------------------------------------
@api_defaults(route_name='polls')
class PollsAPI(View):

    @api_config(request_method='POST')
    @json_body(schemas.Poll, role=ROLES.CREATOR)
    def create_poll(self):
        creator = self.req.session.user
        prompt = self.req.json['prompt']
        poll_key = self.create_poll_key(prompt)

        poll = Poll(creator, prompt=prompt, key=poll_key)
        self.db.add(poll)

        poll.options = []
        for o in self.req.json['options']:
            poll.options.append(Option(creator, poll, o['text']))
        self.db.add_all(poll.options)

        return poll

    def create_poll_key(self, prompt):
        key = KeyCounter.build_key(prompt)
        counter = self.db.query(KeyCounter)\
            .filter(KeyCounter.key == key)\
            .first()
        if counter:
            counter.count += 1
            idx = counter.count
        else:
            counter = KeyCounter(key=key, count=1)
            self.db.add(counter)
            idx = 1
        return '{}-{}'.format(key, idx)


@api_defaults(route_name='poll')
class PollAPI(View):

    @api_config(request_method='GET',
                 permission=PERMISSIONS.READ,
                 login_required=False)
    def get_poll(self):
        return self.ctx.poll

# ------------------------------------------------------------------------------
@api_defaults(route_name='poll_options')
class PollOptionsAPI(View):

    @api_config(request_method='POST')
    def add_poll_option(self):
        creator = self.req.session.user
        poll = self.ctx.poll
        text = self.req.json['text']
        option = Option(creator, poll, text)
        self.db.add(option)
        return option

    @api_config(request_method='GET')
    def get_poll_options(self):
        return {
            'options': self.ctx.poll.options,
        }


@api_defaults(route_name='poll_option')
class PollOptionAPI(View):

    @api_config(request_method='DELETE')
    @json_body(schemas.Poll)
    def delete_option(self):
        self.ctx.option.deleted_at = UTC_TIMESTAMP.now()
        return SUCCESS


# ------------------------------------------------------------------------------
@api_defaults(route_name='votes')
class VotesAPI(View):

    @api_config(request_method='POST')
    @json_body(schemas.Vote, role=ROLES.CREATOR)
    def cast_vote(self):
        option_id = self.req.json['option_id']
        voter = self.req.session.user
        data = self.db.query(Option, Vote)\
            .filter(Option.id == option_id)\
            .outerjoin(Vote, sa.and_(Vote.option_id == Option.id,
                                     Vote.user_id == voter.id))\
            .first()
        if not data:
            raise exc.NotFound('poll not found')
        option, old_vote = data
        if (not old_vote) or (old_vote.option_id != option_id):
            new_vote = Vote(voter, option)
            self.db.add(new_vote)
            return new_vote
        else:
            return old_vote


@api_defaults(route_name='vote')
class VoteAPI(View):
    pass
