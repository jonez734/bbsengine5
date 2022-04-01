#!/usr/bin/env python

from distutils.core import setup
#from setuptools import setup

import time

v = time.strftime("%Y%m%d%H%M")
projectname = "bbsengine5"

setup(
  name=projectname,
  version=v,
  author="zoidtechnologies.com",
  author_email="%s@projects.zoidtechnologies.com" % (projectname),
  py_modules=["bbsengine5", "bbs", "engine"],
  scripts=["bbs", "engine"],
  requires=["ttyio5", "getdate"],
  url="http://bbsengine.org/",
  classifiers=[
    "Programming Language :: Python :: 3.9",
    "Environment :: Console",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Operating System :: POSIX",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Terminals",
  ],
)
