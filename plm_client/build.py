from collections import defaultdict
import productmd.common
from plm_client.rpm import Rpm


class Build(object):
    def __init__(self, nevra):
        """ Represent a build that will have product listings. """
        self.nevra = nevra
        self.nevra_dict = productmd.common.parse_nvra(nevra)
        self.rpms = set()
        self.mappings = defaultdict(dict)  # see map_rpm()

    @property
    def nvr(self):
        return "{name}-{version}-{release}".format(**self.nevra_dict)

    @property
    def arch(self):
        # should always be src ... ? Is this even used?
        assert self.nevra_dict['arch'] == 'src'
        raise NotImplementedError
        return self.nevra_dict['arch']

    def get_rpm(self, nevra):
        found = [rpm for rpm in self.rpms if rpm.nevra == nevra]
        if found:
            return found[0]
        rpm = Rpm(nevra)
        self.rpms.add(rpm)
        return rpm

    def map_rpm(self, variant, rpm, arch):
        """
        Record a mapping of this variant + rpm + architecture.

        :param variant: Variant that ships this RPM file.
        :type variant: ``Variant``

        :param rpm: RPM file that ships this in this Variant.
        :type rpm: ``Rpm``

        :param arch: Architecture for this variant mapping, eg "x86_64".
        :type arch: ``str``
        """
        if rpm.nvr not in self.mappings[variant]:
            self.mappings[variant][rpm.nvr] = {}
        if rpm.arch not in self.mappings[variant][rpm.nvr]:
            self.mappings[variant][rpm.nvr][rpm.arch] = set()
        self.mappings[variant][rpm.nvr][rpm.arch].add(arch)

    def map_debuginfos(self):
        """
        Record mappings for all debuginfo rpms
        """
        for rpm in self.rpms:
            if rpm.is_debuginfo:
                # print('calling map_debuginfo(%s)' % rpm.nevra)
                self.map_debuginfo(rpm)

    def map_debuginfo(self, rpm):
        """
        Record mappings for this debuginfo rpm to this arch.

        products.py maps an arch's debuginfo to *all* variants that have any
        RPMs of the same arch from this build.
        """
        assert rpm.is_debuginfo is True
        # XXX we should not blindly map this rpm to all variants.
        # Only add this rpm to variants that also include one or more rpms of
        # this same arch.
        for variant, mapping in self.mappings.items():
            for arch_data in mapping.values():
                # "arch_data" for this rpm nvr is like:
                #   {'noarch': ['x86_64']}
                #  or
                #   {'i686': ['x86_64'],
                #    'x86_64': ['x86_64']}
                variant_arches = arch_data.get(rpm.arch, [])
                for variant_arch in variant_arches:
                    # print('mapping %s to %s as variant arch %s' % (rpm.nevra, variant, variant_arch))
                    self.map_rpm(variant, rpm, variant_arch)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.nevra)
