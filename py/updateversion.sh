#!/usr/bin/sh

echo '__version__ = "'`git log -1 --format='%H' | cut -c 1-16`'"' > _version.py
echo '__datestamp__ = "'`date +%Y%m%d%H%M`'"' >> _version.py
