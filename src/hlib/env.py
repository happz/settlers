"""
Functions for access library enviroment from external programs. Sets the enviroment up as if code
is present in main library code.

@author:                        Milos Prchlik
@contact:                       U{happz@happz.cz}
@license:                       DPL (U{http://www.php-suit.com/dpl})
"""

import ConfigParser

import hlib
import hlib.database
import hlib.datalayer
import hlib.engine
import hlib.handlers.root
import hlib.log.channels.stderr
import hlib.server

config_defaults = {
  'server':			{
    'host':			'127.0.0.1',
    'port':			8082,
  },
  'log':                        {
    'access_format':		'{date} {time} - {tid} - {request_line} - {response_status} {response_length} - {request_ip} {request_user}'
  },
  'session':			{
    'time':			21600
  }
}

class EnvEngine(hlib.engine.Engine):
  def start(self):
    self.init_stats()

    hlib.event.trigger('engine.Started', None, post = False)

    for s in self.servers:
      s.start()

class Env(object):
  def __init__(self, config_file):
    super(Env, self).__init__()

    config = hlib.ConfigFile(default = config_defaults)
    config.read(config_file)

    stderr = hlib.log.channels.stderr.Channel()

    # pylint: disable-msg=E1101
    hlib.config['log.channels.error'] = stderr

    db_address = hlib.database.DBAddress(config.get('database', 'address'))
    db = hlib.database.DB('main db', db_address)
    db.open()

    app_config                    = hlib.engine.Application.default_config(config.get('server', 'path'))
    app_config['title']           = 'hlib - env'
    app_config['cache.enabled']   = False

    app = hlib.engine.Application('hlib', hlib.handlers.root.Handler(), db, app_config)
    app.channels.access = [stderr]
    app.channels.error  = [stderr]

    app.sessions = hlib.http.session.MemoryStorage(app)
    app.config['sessions.time']           = config.get('session', 'time')
    app.config['sessions.cookie_name']    = config.get('session', 'cookie_name')

    server_config                 = hlib.server.Server.default_config()
    server_config['host']            = config.get('server', 'host')
    server_config['port']            = int(config.get('server', 'port'))
    server_config['max_threads']	= 1
    server_config['app']             = app

    self.engine = EnvEngine([server_config])
    self.engine.start()

    hlib.event.trigger('engine.ThreadStarted', None, server = self.engine.servers[0])

  def quit(self):
    for server in self.engine.servers:
      server.stop()

    hlib.event.trigger('engine.Halted', None)
