#!/data/virtualenv/settlers/bin/python

import ConfigParser
import formencode
import handlers
import functools
import getopt
import ipaddr
import sys
import handlers.root
import traceback
import types
import syslog
import time
import os
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

#
# Default values for config file options
#
config_defaults = {
  'server':			{
    'host':			'127.0.0.1',
    'port':			8082,
    'pool.max':			10
  },
  'log':			{
    'access_format':		'{date} {time} - {tid} - {request_line} - {response_status} {response_length} - {request_ip} {request_user}'
  },
  'session':			{
    'time':			3600
  },
  'system_games':		{
    'limit':			20,
    'sleep':			3
  },
  'cache':			{
    'enabled':			False,
    'dont_cache':		''
  },
  'stats':			{
    'games.window':		31449600,
    'games.threshold':		20
  }
}

def on_request_started(e):
  # pylint: disable-msg=W0613
  hruntime.i18n = hruntime.dbroot.localization.languages['cz']

  if hruntime.user and hruntime.user.is_on_vacation and hruntime.request.config.get('survive_vacation', None) != True:
    raise hlib.http.Redirect('/vacation/')

hlib.event.Hook('engine.RequestStarted', 'settlers_generic', on_request_started)

def on_app_config(app, config):
  app.config['system_games.limit']  = int(config.get('system_games', 'limit'))
  app.config['system_games.sleep']  = int(config.get('system_games', 'sleep'))

import hlib.runners.standalone
hlib.runners.standalone.main(handlers.root.Handler(), config_defaults, on_app_config)
