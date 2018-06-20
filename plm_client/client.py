import xmlrpclib
import requests


class Client(object):
    """ Product Listings Manager API client """
    def __init__(self, url):
        """
        :param url: product-listings server to query.
        :type url: ``str``
        """
        self.url = url

    def get_product_listings(self, product_label, nvr):
        """
        Call the product-listings API endpoint.

        If this client's ``url`` attribute contains the strings "brewhub" or
        "xmlrpc", this method will call the XML-RPC method. Otherwise, the
        client will use the REST API method.

        :param product_label: composedb's "product label", eg. "RHEL-7-CEPH-2"
                              or "RHEL-7.5"
        :type product_label: ``str``

        :param nvr: Koji build Name-Version-Release to query.
        :type nvr: ``str``

        :return: product listings data
        :rtype: ``dict``
        """
        if 'brewhub' in self.url or 'xmlrpc' in self.url:
            return self._xmlrpc('getProductListings', product_label, nvr)
        endpoint = '/product-listings/%s/%s'
        return self._get(endpoint, product_label, nvr)

    def _xmlrpc(self, method, *args):
        """
        Call an xmlrpc method on the product-listings-manager server.

        :param method: name of the method to call, eg. "getProductListings"
        :type method: ``str``

        :param *args: arguments to pass to the XML-RPC method.
        :type *args: ``list``

        :return: data from XML-RPC method call
        :rtype: built-in type like ``dict``
        """

        server = xmlrpclib.ServerProxy(self.url)
        # ug, hard-coding here:
        if 'brewhub' in self.url:
            print('brew call getProductListings %s %s' % tuple(args))
        else:
            print('xmlrpc call getProductListings %s %s' % tuple(args))
        rpc = getattr(server, method)
        result = rpc(*args)
        return result

    def _get(self, endpoint, *args):
        """
        Call a REST method on the product-listings-manager server.

        :param endpoint: endpoint under ``url``, eg.
                         "/product-listings/%s/%s"
        :type method: ``str``

        :param *args: arguments to pass to the endpoint format string
        :type *args: ``list``

        :return: data from REST method call
        :rtype: built-in type like ``dict``
        """
        url = self.url + endpoint % args
        print('GET %s' % url)
        result = requests.get(url)
        result.raise_for_status()
        data = result.json()
        return data
