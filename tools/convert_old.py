import getopt
import sys

import convert

import hlib
import hlib.env
import hlib.sql

# pylint: disable-msg=F0401
import hruntime

def usage():
  print """convert.py [OPTIONS]
  -h			Print this info
  -c <config>		Config file
  -t <trees>		Tree names, separated by comma (%s)
""" % (', '.join(convert.CONVERTORS.keys()))

def run():
  config_file = None
  trees = None

  if len(sys.argv) <= 1:
    usage()
    sys.exit(0)

  optlist, args = getopt.getopt(sys.argv[1:], 'c:ht:')

  for o in optlist:
    if o[0] == '-c':
      config_file = o[1]

    elif o[0] == '-h':
      usage()
      sys.exit(0)

    elif o[0] == '-t':
      trees = [t.strip() for t in o[1].split(',')]

  hlib.env.init_env(config_file)

  sqldb = hlib.sql.DataBase(host = 'localhost', unix_socket = '/var/run/mysqld/mysqld.sock', user = 'settlers', passwd = 'EudaiNgaiW5aiyaM', db = 'settlers-old')
  sqldb.open()
  sql = sqldb.connect()

  for tree_name in trees:
    tree = convert.CONVERTORS[tree_name](sql)

    print 'Beginning conversion of \'%s\'' % tree_name
    tree.run()
    tree.commit()
    print 'Done.'

if __name__ == '__main__':
  run()
