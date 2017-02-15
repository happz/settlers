__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import getopt
import sys

import hlib.runners

config_file = None

def usage():
  print sys.argv[0] + """ <options>

where options can be:

  -h              Print this message and quit
  -c config_file  Specify different path to config file

"""
  sys.exit(0)

def main(root, config_defaults):
  optlist, _ = getopt.getopt(sys.argv[1:], 'c:h')

  for o in optlist:
    if o[0] == '-h':
      usage()

    elif o[0] == '-c':
      config_file = o[1]

    runner = hlib.runners.Runner(config_file, root, config_defaults = config_defaults)
    runner.run()
