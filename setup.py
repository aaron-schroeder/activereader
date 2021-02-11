# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read(rel_path):
  """Read a file so python does not have to import it.
  
  Inspired by (taken from) pip's `setup.py`.
  """
  here = os.path.abspath(os.path.dirname(__file__))
  # intentionally *not* adding an encoding option to open, See:
  #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
  with open(os.path.join(here, rel_path), 'r') as fp:
    return fp.read()


def get_version(rel_path):
  """Manually read through a file to retrieve its `__version__`.
  
  Inspired by (taken from) pip's `setup.py`.
  """
  for line in read(rel_path).splitlines():
    if line.startswith('__version__'):
      # __version__ = '0.0.1'
      delim = "'" if "'" in line else '"'
      return line.split(delim)[1]
  raise RuntimeError('Unable to find version string.')


with open('README.rst') as f:
  readme = f.read()

with open('LICENSE') as f:
  license = f.read()

# Could this be outsourced somehow? find_packages maybe?
pkg_name = 'activereader'

setup(
  name=pkg_name,
  version=get_version('%s/__init__.py' % pkg_name),
  description='description placeholder',
  long_description=readme,
  author='Aaron Schroeder',
  #author_email='',
  install_requires = [
    'lxml==4.6.2',
    'pandas==1.2.2',
    'python-dateutil==2.8.1',
  ],
  url='https://github.com/aaron-schroeder/py-activityreaders',
  license=license,
  packages=find_packages(exclude=('tests', 'docs'))
)

