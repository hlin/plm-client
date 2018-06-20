import productmd


class Rpm(object):
    def __init__(self, nevra):
        """ Represent a single RPM in a build. """
        self.nevra = nevra
        self.nevra_dict = productmd.common.parse_nvra(nevra)
        self.arch_listings = []

    @property
    def name(self):
        """ For example "xsom" """
        return self.nevra_dict['name']

    @property
    def nvr(self):
        """ For example "xsom-0-10.20110809svn.el7" """
        return "{name}-{version}-{release}".format(**self.nevra_dict)

    @property
    def arch(self):
        """ For example "i686" or "x86_64" """
        return self.nevra_dict['arch']

    @property
    def is_debuginfo(self):
        """ Return True if this is a debuginfo rpm, False otherwise. """
        if self.name.endswith('-debuginfo'):
            return True
        if self.name.endswith('-debuginfo-common'):
            return True
        return False

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.nevra)
