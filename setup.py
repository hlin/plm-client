import re
import os
from setuptools import setup, find_packages


readme = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(readme).read()


def read_module_contents():
    with open('plm_client/__init__.py') as app_init:
        return app_init.read()


module_file = read_module_contents()
metadata = dict(re.findall(r"__([a-z]+)__\s*=\s*'([^']+)'", module_file))
version = metadata['version']

setup(name="plm-client",
      version=version,
      description='product-listings-manager api client',
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Intended Audience :: Developers',
                   'Operating System :: POSIX',
                   'Programming Language :: Python',
                   'Topic :: Software Development',
                   ],
      keywords='product compose',
      author='Ken Dreyer',
      author_email='kdreyer@redhat.com',
      url='https://github.com/ktdreyer/plm-client',
      license='MIT',
      long_description=LONG_DESCRIPTION,
      packages=find_packages(),
      scripts=['bin/plm-check-compose', 'bin/plm-get-prod-listings'],
      install_requires=[
        'productmd',
        'requests',
      ],
      tests_require=[
          'pytest',
      ],
)
