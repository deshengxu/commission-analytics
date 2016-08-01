#!/usr/bin/env python

# ...

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from ca import __version__

setup(name='ca.py',
      version=__version__,
      description='ca.py: commission analytics',
      author='Desheng Xu',
      author_email='dxu@ptc.com',
      maintainer='Desheng Xu',
      maintainer_email='dxu@ptc.com',
      url=' ',
      packages=['ca'],
      long_description="A python tool for commission what-if analysis.",
      license="Public domain",
      platforms=["any"],
      install_requires=['matplotlib','pandas'],
      )
