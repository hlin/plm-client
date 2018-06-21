product-listings-manager client
===============================

Python client to the product-listings-manager HTTP interface.

Example:

.. code-block:: python

    from plm_client import Client
    from plm_client.constants import SERVERS

    c = Client('http://prodlistings-dev1.usersys.redhat.com/api/v1.0')
    # or:
    c = Client(SERVERS['dev1'])

    listings = c.get_product_listings('RHEL-7.6', 'libpsm2-10.3.8-3.el7')
    print(listings)
    # Prints the prod-listings for this build, for example
    # {'Workstation-optional-7.6':
    #    {'libpsm2-devel-10.3.8-3.el7': {'x86_64': ['x86_64']},
    #     ...
    #     }
    #    ...
    # }


plm-check-compose
-----------------

This tool sanity-checks a compose's layout against product-listings-manager.

The idea is to put a bit of load on the product-listings-manager web service
and perform a simple "integration" test.

For each build in the compose, ``plm-check-compose`` will:

* Query the "product-listings" API for the product + build

* Ensure that every RPM is present in prod-listings and routed to the
  appropriate destination arches.

TODO:

* Make multiple calls against different product-listings-manager environments
  (brew, dev, stage, prod) and compare the data to identify any differences
  in implementations.

* Measure and store the (wall clock) response time for each call in order to
  track the service's performance.

plm-get-product-listings
------------------------

This is a drop-in replacement for the ``brew call getProductListings`` CLI
command.

.. code-block:: shell

   $ plm-get-prod-listings -h
     usage: plm-get-prod-listings [-h] product_label build

     positional arguments:
       product_label  eg. "RHEL-7.6"
       build          build NVR, eg "nmap-6.40-13.el7"

   $ plm-get-prod-listings RHEL-7.6 nmap-6.40-13.el7
     ...(pretty-prints dict here)
