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
import hlib.log.channels.stderr
import hlib.log.channels.file

import handlers.root
import lib.datalayer

import events.system

# pylint: disable-msg=F0401
import hruntime

#import thirdparty.dowser

cmd_options = {
  'config_file':	'settlers.conf'
}

#
# Default values for config file options
#
config_defaults = {
  'server':			{
    'host':			'127.0.0.1',
    'port':			8082,
  },
  'log':			{
    'access_format':		'{date} {time} - {tid} - {request_line} - {response_status} {response_length} - {request_ip} {request_user}'
  },
  'session':			{
    'time':			21600
  },
  'system_games':		{
    'limit':			20,
    'sleep':			3
  }
}

def on_request_started(e):
  # pylint: disable-msg=W0613
  hruntime.i18n = hruntime.dbroot.localization.languages['cz']

  if hruntime.user and hruntime.user.is_on_vacation and hruntime.request.config.get('survive_vacation', None) != True:
    raise hlib.http.Redirect('/vacation/')

hlib.event.Hook('engine.RequestStarted', 'settlers_generic', on_request_started)

def main():
  """
  Main startup function of Settlers engine.
  """

  config = hlib.ConfigFile(default = config_defaults)
  config.read(cmd_options['config_file'])

  stderr = hlib.log.channels.stderr.Channel()
  access = hlib.log.channels.file.Channel(os.path.join(config.get('server', 'path'), 'logs', 'access.log'))
  error  = hlib.log.channels.file.Channel(os.path.join(config.get('server', 'path'), 'logs', 'error.log'))

  hlib.config['log.channels.error'] = stderr

  db_address = hlib.database.DBAddress(config.get('database', 'address'))
  db = hlib.database.DB('main db', db_address, cache_size = 35000)
  db.open()

  app_config			= hlib.engine.Application.default_config(config.get('server', 'path'))
  app_config['title']		= config.get('web', 'title')
  app_config['label']		= 'Settlers'
  app_config['cache.enabled']	= False

  app = hlib.engine.Application('settlers', handlers.root.Handler(), db, app_config)

  app.sessions = hlib.http.session.FileStorage(config.get('session', 'storage_path'), app)
  app.config['sessions.time']		= config.get('session', 'time')
  app.config['sessions.cookie_name']	= config.get('session', 'cookie_name')

  app.config['log.access.format']	= config.get('log', 'access_format')
  app.channels.access = [stderr, access]
  app.channels.error  = [stderr, error]

  app.config['system_games.limit']	= int(config.get('system_games', 'limit'))
  app.config['system_games.sleep']	= int(config.get('system_games', 'sleep'))

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
