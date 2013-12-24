#!/data/virtualenv/settlers/bin/python

import hlib.events
import hlib.http

import handlers.root

# pylint: disable-msg=F0401
import hruntime  # @UnresolvedImport

#
# Default values for config file options
#
config_defaults = {
  'server':			{
    'host':			'127.0.0.1',
    'port':			8082,
    'queue.workers':			10
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

hlib.events.Hook('engine.RequestStarted', on_request_started)

def on_app_config(app, config):
  app.config['system_games.limit']  = int(config.get('system_games', 'limit'))
  app.config['system_games.sleep']  = int(config.get('system_games', 'sleep'))

import hlib.runners.standalone
hlib.runners.standalone.main(handlers.root.Handler(), config_defaults, on_app_config)
