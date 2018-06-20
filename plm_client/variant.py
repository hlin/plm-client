class Variant(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.name)
