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
        self.variants = set()
        self.builds = set()

    def get_build(self, nevra):
        """
        Get a new or existing ``Build`` object for this product.

        :param name: Variant name according to composedb.
        :type name: ``str``

        :return: Variant
        :rtype: ``plm_client.variant.Variant``
        """
        found = [build for build in self.builds if build.nevra == nevra]
        if found:
            return found[0]
        build = Build(nevra)
        self.builds.add(build)
        return build

    def get_variant(self, name):
        """
        Get a new or existing ``Variant`` object for this product.

        :param name: Variant name according to composedb.
        :type name: ``str``

        :return: Variant
        :rtype: ``plm_client.variant.Variant``
        """
        found = [variant for variant in self.variants if variant.name == name]
        if found:
            return found[0]
        variant = Variant(name)
        self.variants.add(variant)
        return variant

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
                    # Same issue with xsom and rngom
                    #if not build_nevra.startswith('xsom'):
                    #    continue
                    build = product.get_build(build_nevra)
                    # build.nvr is like "ceph-12.2.5-25.el7cp"
                    for rpm_nevra in rpm_data:
                        rpm = build.get_rpm(rpm_nevra)
                        rpm.arch_listings.append({variant: arch})
                        build.map_rpm(variant, rpm, arch)
                    # Map any debuginfo rpms explicitly.
                    # (We must do this after the end of the previous loop here,
                    # after build.mappings has been populated.)
                    build.map_debuginfos()
        return product
