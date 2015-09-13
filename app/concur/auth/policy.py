from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import CallbackAuthenticationPolicy
from zope.interface import implementer


@implementer(IAuthenticationPolicy)
class SessionAuthenticationPolicy(CallbackAuthenticationPolicy):

    def __init__(self, debug=False):
        super(SessionAuthenticationPolicy, self).__init__()
        self.__class__.callback = self.__class__.groups
        self.__class__.debug = debug

    def remember(self, request, user, **kwargs):
        """
        Return a set of headers suitable for 'remembering' the principal named
        principal when set in a response. An individual authentication policy
        and its consumers can decide on the composition and meaning of **kw.
        """
        request.session.remember(user)

    def forget(self, request):
        """
        Return a set of headers suitable for 'forgetting' the current user on
        subsequent requests.
        """
        request.session.invalidate()

    def unauthenticated_userid(self, request):
        """
        Return the unauthenticated userid. This method performs the same duty
        as authenticated_userid but is permitted to return the userid based
        only on data present in the request; it needn't (and shouldn't) check
        any persistent store to ensure that the user record related to the
        request userid exists.
        """
        user = request.session.user
        return user.public_id if user else None

    @classmethod
    def groups(cls, user_id, request):
        return request.session.groups
