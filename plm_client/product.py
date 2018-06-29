from collections import defaultdict
from plm_client.variant import Variant
from plm_client.build import Build


class ProductListing(defaultdict):
    """
    getProductListings result for a product label + build nvr.

    {ProductVariantListing("Server-RHEL-7-RHCEPH-3.1-Tools"={})

    First-level keys are all the composedb variant names.
    """
    def __init__(self, *args, **kwargs):
        super(ProductListing, self).__init__(*args, **kwargs)
        self.default_factory = lambda: ProductVariantListing(dict)


class ProductVariantListing(defaultdict):
    """
    getProductListings result for a single variant + build nvr.

    First-level keys are the rpm names.
    """
    def __init__(self, *args, **kwargs):
        super(ProductVariantListing, self).__init__(*args, **kwargs)
        self.default_factory = lambda: defaultdict(dict)


class Product(object):
    def __init__(self):
        self._variants = {}
        self._builds = {}

    @property
    def builds(self):
        return self._builds.values()

    @property
    def variants(self):
        return self._builds.values()

    def get_build(self, nevra):
        """
        Get a new or existing ``Build`` object for this product.

        :param nevra: Build epoch name-version-release arch.
        :type nevra: ``str``

        :return: Build
        :rtype: ``plm_client.build.Build``
        """
        if nevra in self._builds:
            return self._builds[nevra]
        self._builds[nevra] = Build(nevra)
        return self._builds[nevra]

    def get_variant(self, name):
        """
        Get a new or existing ``Variant`` object for this product.

        :param name: Variant name according to composedb.
        :type name: ``str``

        :return: Variant
        :rtype: ``plm_client.variant.Variant``
        """
        if name in self._variants:
            return self._variants[name]
        self._variants[name] = Variant(name)
        return self._variants[name]

    @classmethod
    def from_compose(klass, compose):
        """
        Populate this product's expected mappings based on a compose.

        :param compose: Compose to read.
        :type compose: ``plm_client.compose.Compose``

        :return: Product class that references all the builds. The ".builds"
                 attribute will have all the builds for this compose, along
                 with the expected prod-listings.
        :rtype: ``plm_client.product.Product``
        """
        product = klass()

        for variant_name, variant_data in compose.rpms.rpms.items():
            # "variant_name" is the compose's variant, like "Server" or
            # "Tools".
            # "variant_data" is the dict of all arches and builds for this
            # variant.

            # Get the composedb name, eg. "Server-RHEL-7-RHCEPH-3.1-Tools"
            composedb_variant = compose.composedb_variant(variant_name)
            variant = product.get_variant(composedb_variant)

            for arch, arch_data in variant_data.items():
                # "arch" is this variant's arch, eg. "x86_64".
                for build_nevra, rpm_data in arch_data.items():
                    # XXX hack for testing
                    # Some issues with xsom, rngom, nuxwdog
                    #if not build_nevra.startswith('nuxwdog'):
                    #    continue
                    build = product.get_build(build_nevra)
                    # build.nvr is like "ceph-12.2.5-25.el7cp"
                    for rpm_nevra in rpm_data:
                        rpm = build.get_rpm(rpm_nevra)
                        rpm.arch_listings.append({variant: arch})
                        build.map_rpm(variant, rpm, arch)
                    # Map any src and debuginfo rpms explicitly.
                    # (We must do this after the end of the previous loop here,
                    # after build.mappings has been populated.)
                    build.map_srcs()
                    build.map_debuginfos()
        return product
