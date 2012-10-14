#!/usr/bin/python

import coffeescript
import codecs
import sys

if len(sys.argv) != 2:
  print >> sys.stderr, 'coffee-compile <file>'
  sys.exit(1)

with codecs.open(sys.argv[1], 'r', 'utf-8') as f:
  print '\n'.join(coffeescript.compile(f.read()).split('\n')[1:-2])
