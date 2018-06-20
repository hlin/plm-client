from __future__ import print_function
from collections import defaultdict
from pprint import pprint
from plm_client.product import Product


def check_compose(compose, client):
    """
    Verify a compose against product listings.

    :param compose: Compose to verify.
    :type compose: ``plm_client.compose.Compose``

    :param client: product-listings server client to query.
    :type client: ``plm_client.Client``
    """
    # Iterate through all the builds for this product.
    product = Product.from_compose(compose)
    for build in product.builds:
        expected = defaultdict(dict)
        for variant, mapping in build.mappings.items():
            for nvr, rpm_arches in mapping.items():
                if nvr not in expected[variant.name]:
                    expected[variant.name][nvr] = {}
                for rpm_arch, variant_arches in rpm_arches.items():
                    dest_arches = list(variant_arches)
                    expected[variant.name][nvr][rpm_arch] = dest_arches
        result = client.get_product_listings(compose.product_label, build.nvr)
        # XXX: RHEL composes have no "Alt" or "Buildroot" variants. Something
        # else puts these into composedb. (some other separate RHEL composes?)
        for maybe_delete_variant in list(result.keys()):
            if "Alt" in maybe_delete_variant:
                del result[maybe_delete_variant]
            if "Buildroot" in maybe_delete_variant:
                del result[maybe_delete_variant]

        # Kinda hacky comparison stuff here; need to refactor.
        if result != expected:
            pprint(result)
            pprint(dict(expected))
            print('XXX diff found:')
            diff = set(result) ^ set(expected)
            if diff:
                pprint(diff)
            for k in result:
                if result[k] != expected[k]:
                    print('XXX diff found in key %s' % k)
                    for kk in result[k]:
                        if result[k][kk] != expected[k][kk]:
                            print('XXX diff found in inner key %s' % kk)
        assert result == expected
