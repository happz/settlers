#!/usr/bin/python

import ConfigParser
import formencode
import handlers
import functools
import getopt
import sys
import handlers.root
import traceback
import types
import syslog
import time
import os.path

import hlib
import hlib.auth
import hlib.database
import hlib.handlers.root
import hlib.http.session
import hlib.engine
import hlib.error
import hlib.event
import hlib.i18n
import hlib.log.channels.sysloger
import hlib.server

import handlers.root
import lib.datalayer

import events.system

# pylint: disable-msg=F0401
import hruntime

#import thirdparty.dowser

cmd_options = {
  'config_file':	'settlers.conf'
}

def __on_request_started(e):
  hruntime.localization = hruntime.dbroot.localization.languages['cz']

  if hruntime.user:
    if hruntime.user.is_on_vacation:
      if hruntime.request.config.get('survive_vacation', None) != True:
        raise hlib.server.HTTPRedirect('/vacation/')

hlib.event.Hook('engine.RequestStarted', 'settlers_generic', __on_request_started)

def main():
  """
  Main startup function of Settlers engine.
  """

  config = ConfigParser.ConfigParser()
  config.read(cmd_options['config_file'])

  # logs
  import hlib.log.channels.stderr, hlib.log.channels.file

  stderr = hlib.log.channels.stderr.Channel()
  access = hlib.log.channels.file.Channel(os.path.join(config.get('server', 'path'), 'logs', 'access.log'))
  error  = hlib.log.channels.file.Channel(os.path.join(config.get('server', 'path'), 'logs', 'error.log'))

  hlib.config['log.channels.error'] = stderr

  formencode.api.set_stdtranslation(domain = 'FormEncode', languages = ['cs'])

  db_address = hlib.database.DBAddress(config.get('database', 'address'))
  db = hlib.database.DB(db_address)
  db.open()

  app_config			= hlib.engine.Application.default_config(config.get('server', 'path'))
  app_config['title']		= config.get('web', 'title')
  app_config['cache.enabled']	= False

  app = hlib.engine.Application('settlers', handlers.root.Handler(), db, app_config)

  app.sessions = hlib.http.session.FileStorage(os.path.join('/', 'tmp', 'settlers-sessions.dat'), app)
  app.config['sessions.time']          = 2 * 86400

  app.channels.access = [stderr, access]
  app.channels.error  = [stderr, error]

  server_config			= hlib.server.Server.default_config()
  server_config['server']	= config.get('server', 'host')
  server_config['port']		= int(config.get('server', 'port'))
  server_config['app']		= app

  engine = hlib.engine.Engine([server_config])

  print 'Starting...'
  engine.start()

def usage():
  print """settlers.py <options>

where options can be:

  -h			Print this message and quit
  -c config_file	Specify different path to config file. Default is 'settlers.conf'

"""
  sys.exit(0)

hruntime.tid = None

optlist, args = getopt.getopt(sys.argv[1:], 'c:h')

for o in optlist:
  if o[0] == '-h':
    usage()

  elif o[0] == '-c':
    cmd_options['config_file'] = o[1]

if __name__ == '__main__':
  main()
