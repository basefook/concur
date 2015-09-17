class enum(tuple):
    def __new__(cls, values):
        return super(enum, cls).__new__(cls, values)

    def __init__(self, values):
        for k in values.split():
            setattr(self, k, k)


class const_object(object):
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise AttributeError('Cannot reset constant attribute.')
        else:
            super(const_object, self).__setattr__(key, value)


class const_dict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise KeyError('Cannot reset constant value.')
        else:
            super(const_dict, self).__setitem__(key, value)
