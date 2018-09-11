import tempfile
import subprocess
try:
    from xmlrpc.client import dumps
except ImportError:
    from xmlrpclib import dumps

"""
This script will benchmark getProductListings results with ab.
"""

LABEL = 'RHEL-6-Server-EXTRAS-6'
BUILD = 'dumb-init-1.2.0-1.20170802gitd283f8a.el6'


def serialize(method, params):
    """ Return a XML-RPC representation of this method and parameters. """
    return dumps(params, method).replace("\n", '')


def run(cmd):
    """ Run a command, with logging. """
    print('+ ' + ' '.join(cmd))
    subprocess.check_call(cmd)


def get(url, requests=20):
    """ GET a URL with ab. """
    cmd = ['ab',
           '-T', 'application/json',
           '-c', '1',
           '-n', str(requests),
           url]
    run(cmd)


def post(url, content, requests=20):
    """ POST a URL with ab. """
    with tempfile.NamedTemporaryFile(mode='w+') as temp:
        temp.write(content)
        temp.flush()
        cmd = ['ab',
               '-p', temp.name,
               '-c', '1',
               '-n', str(requests),
               url]
        run(cmd)


def benchmark_xmlrpc(url):
    content = serialize('getProductListings', (LABEL, BUILD))
    post(url, content)


def benchmark_rest(url):
    template = '{base}/api/v1.0/product-listings/{label}/{build}'
    fullurl = template.format(base=url, label=LABEL, build=BUILD)
    get(fullurl)


#benchmark_xmlrpc('http://prodlistings-dev1.usersys.redhat.com/xmlrpc')
#benchmark_xmlrpc('https://prodlistings.stage.engineering.redhat.com/xmlrpc')
#benchmark_xmlrpc('https://brewhub.stage.engineering.redhat.com/brewhub')
#benchmark_xmlrpc('https://brewhub.engineering.redhat.com/brewhub')
#benchmark_rest('http://prodlistings-dev1.usersys.redhat.com')
#benchmark_rest('https://prodlistings.stage.engineering.redhat.com')
#benchmark_rest('http://localhost:5000')
