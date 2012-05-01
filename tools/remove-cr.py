#!/usr/bin/python2.7

import sys

if len(sys.argv) != 2:
  print 'remove-cr.py <filename>'
  sys.exit(0)

with open(sys.argv[1], 'rb') as f:
  data = f.read()

sys.stdout.write(data.replace('\r\n', '\n'))
