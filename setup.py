#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name='libnodave',
  version='1.0',
  description='LibNoDave C lib wrapper',
  long_description=read('README.md'),
  author='Wouter DHaeseleer',
  author_email='info@netdata.be',
  url='http://netdata.be',
  dependency_links = ['https://github.com/netdata/libnodave/zipball/master'],
  packages=['libnodave'],
)
