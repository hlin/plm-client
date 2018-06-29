import productmd.compose


class Compose(productmd.compose.Compose):
    """ Subclass productmd's Compose with helpers for prod-listings """

    @property
    def product_label(self):
        """
        Translate a compose's product metadata to a composedb "product label".

        It's basically impossible to generalize this into something that works
        for all Red Hat products, but we can at least try for RHEL and RHCEPH.

        The translation from compose variants to product labels is done with
        distill-utils' "compose-composedb-import" CLI tool, using the
        arguments:
           --product-override (eg. RHEL-7-CEPH-3)
           --version-override (eg. 3)

        :return: composedb's "product label" eg "RHEL-7-CEPH-2".
        :rtype: ``str``
        """
        product = self.info.release.short
        version = self.info.release.version
        if self.info.release.is_layered:
            tmpl = '{os}-{osver}-{product}-{version}'
            return tmpl.format(
                os=self.info.base_product.short,
                osver=self.info.base_product.version,
                product=product,
                version=version,
            )
        return '%s-%s' % (product, version)

    def composedb_variant(self, variant):
        """
        Translate a compose's variant name to a composedb variant name.

        It's impossible to generalize this into something that works for all
        Red Hat products, but we can at least try for RHEL and RHCEPH.

        The translation from compose variants to product labels is done with
        distill-utils' "compose-composedb-import" CLI tool, using the argument:
           --rename-variant

        :param variant: Name of the compose's variant to translate. eg.
                        "Server" or "Tools"
        :type variant: ``str``

        :return: composedb's "variant". Examples:
                  "Server-7.5" or "Server-7.5-optional" for RHEL 7.
                  "Server-RH7-CEPH-TOOLS-2" for RHCEPH 2.
        :rtype: ``str``
        """
        if self.info.release.short == 'RHEL':
            return '%s-%s' % (variant, self.info.release.version)
        if self.info.release.short == 'RHCEPH':
            # eg:
            # "Server-RHEL-7-RHCEPH-3.1-MON"
            # "Server-RHEL-7-RHCEPH-3.1-OSD"
            # "Server-RHEL-7-RHCEPH-3.1-Tools"
            bp_variant = 'Server'
            tmpl = '{bp_variant}-{bp_product}-{bp_version}-{product}-{version}-{variant}'
            return tmpl.format(
                bp_product=self.info.base_product.short,
                bp_version=self.info.base_product.version,
                bp_variant=bp_variant,
                product=self.info.release.short,
                version=self.info.release.version,
                variant=variant,
            )
        raise NotImplementedError(self.info.release.short)
