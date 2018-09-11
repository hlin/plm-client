import tempfile
import subprocess
from textwrap import dedent
try:
    from xmlrpc.client import dumps
    from urllib.parse import urlparse
except ImportError:
    from xmlrpclib import dumps
    from urlparse import urlparse

"""
This script will benchmark getProductListings results with httperf.
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


def get(url, sessions=100):
    """ GET a URL with httperf. """
    o = urlparse(url)
    ssl = None
    if o.scheme == 'https':
        ssl = '--ssl'
    port = o.port
    if port is None:
        if o.scheme == 'http':
            port = 80
        elif o.scheme == 'https':
            port = 443
        else:
            raise RuntimeError(o)
    cmd = ['httperf',
           '--hog',
           '--server', o.hostname,
           '--port', str(port),
           #'--add-header', 'Accept: application/json\n',
           '--uri', o.path,
           '--num-conns', str(sessions)]
    if ssl:
        cmd.append(ssl)
    run(cmd)


def post(url, content, sessions=100):
    """ POST a URL with httperf. """
    o = urlparse(url)
    ssl = None
    if o.scheme == 'https':
        ssl = '--ssl'
    port = o.port
    if port is None:
        if o.scheme == 'http':
            port = 80
        elif o.scheme == 'https':
            port = 443
        else:
            raise RuntimeError(o)
    content = content.replace('"', '\\"')
    template = dedent("""
{path} method=POST contents="{content}"
""")
    config = template.format(path=o.path, content=content)
    print(config)
    with tempfile.NamedTemporaryFile(mode='w+') as temp:
        temp.write(config)
        temp.flush()
        wsesslog = '%s,0,%s' % (sessions, temp.name)
        cmd = ['httperf',
               '--hog',
               '--server', o.hostname,
               '--port', str(port),
               ssl,
               '--method', 'POST', '--wsesslog', wsesslog]
        if ssl:
            cmd.append(ssl)
        run(cmd)


def benchmark_xmlrpc(url):
    content = serialize('getProductListings', (LABEL, BUILD))
    post(url, content)


def benchmark_rest(url):
    template = '{base}/api/v1.0/product-listings/{label}/{build}'
    fullurl = template.format(base=url, label=LABEL, build=BUILD)
    get(fullurl)


#benchmark_xmlrpc('http://prodlistings-dev1.usersys.redhat.com/xmlrpc')
#benchmark_xmlrpc('https://brewhub.stage.engineering.redhat.com/brewhub')
#benchmark_xmlrpc('https://brewhub.engineering.redhat.com/brewhub')
#benchmark_rest('http://prodlistings-dev1.usersys.redhat.com')
benchmark_rest('https://prodlistings.stage.engineering.redhat.com')
#benchmark_rest('http://localhost:5000')
