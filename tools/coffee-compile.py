#!/usr/bin/python

import coffeescript
import sys

if len(sys.argv) != 2:
  print >> sys.stderr, 'coffee-compile <file>'
  sys.exit(1)

with open(sys.argv[1], 'r') as f:
  print '\n'.join(coffeescript.compile(f.read()).split('\n')[1:-2])
