import jsl

from concur.constants import ROLES


# common JSL variables
true_if_creator = jsl.Var({ROLES.CREATOR: True})


class Document(jsl.Document):
    pass


class User(Document):
    email = jsl.EmailField(required=true_if_creator)
    password = jsl.StringField(required=true_if_creator)


class Option(Document):
    text = jsl.StringField(required=true_if_creator)


class Poll(Document):
    prompt = jsl.StringField(required=true_if_creator)
    options = jsl.ArrayField(items=jsl.DocumentField(Option),
                             required=true_if_creator,
                             min_items=2)


class Vote(Document):
    option_id = jsl.StringField(required=true_if_creator)
    is_public = jsl.BooleanField(required=False)
