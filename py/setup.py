#!/usr/bin/env python

from distutils.core import setup

import time

v = time.strftime("%Y%m%d%H%M")
projectname = "bbsengine5"

setup(
  name=projectname,
  version=v,
  author="zoid technologies",
  author_email="%s@projects.zoidtechnologies.com" % (projectname),
  py_modules=["bbsengine5"],
  scripts=[],
  requires=["ttyio4"],
  url="http://bbsengine.org/",
  classifiers=[
    "Programming Language :: Python :: 3.7",
    "Environment :: Console",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Operating System :: POSIX",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Terminals",
  ],
)
