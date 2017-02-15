__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import ConfigParser
import ipaddr
import os.path
import signal
import sys

import hlib.database
import hlib.engine
import hlib.events
import hlib.http.session
import hlib.log.channels.file
import hlib.log.channels.stdout
import hlib.log.channels.stderr
import hlib.server
import hlib.ui.templates.Mako

import hruntime  # @UnresolvedImport

hruntime.tid = 'Master thread'

class ConfigFile(ConfigParser.ConfigParser):
  def __init__(self, default = None):
    ConfigParser.ConfigParser.__init__(self)

    self.default = default or {}

  def get(self, section, option):
    if self.has_option(section, option):
      return ConfigParser.ConfigParser.get(self, section, option)

    if section not in self.default:
      raise ConfigParser.NoSectionError(section)

    if option not in self.default[section]:
      raise ConfigParser.NoOptionError(option, section)

    return self.default[section][option]

class Runner(object):
  def on_sighup(self, signum, frame):
    if signum != signal.SIGHUP:
      return

    hlib.events.trigger('system.LogReload', None)

  def on_sigusr1(self, signum, frame):
    if signum != signal.SIGUSR1:
      return

    hlib.events.trigger('system.SystemReload', None)

    os.execv(sys.argv[0], sys.argv[:])

  def __init__(self, config_file, root, config_defaults = None):
    super(Runner, self).__init__()

    config = ConfigFile(default = config_defaults)
    config.read(config_file)

    # Setup database
    db_address = hlib.database.DBAddress(config.get('database', 'address'))
    db = hlib.database.DB('main db', db_address, cache_size = config.getint('database', 'cache_size'), pool_size = config.getint('server', 'queue.workers') + 1)
    db.open()

    # Create application
    app_config = hlib.engine.Application.default_config(config.get('server', 'path'))
    app_config['title'] = config.get('web', 'title')
    app_config['label'] = config.get('web', 'label')

    # Various pieces of configuration
    app_config['cache.enabled'] = config.getboolean('cache', 'enabled')
    for token in config.get('cache', 'dont_cache').split(','):
      app_config['cache.dont_cache.' + token.strip()] = True

    app_config['hosts'] = {}
    if config.has_section('hosts'):
      for option in config.options('hosts'):
        addresses = config.get('hosts', option)
        app_config['hosts'][option] = [(ipaddr.IPNetwork(addr.strip()) if '/' in addr else ipaddr.IPAddress(addr.strip())) for addr in addresses.strip().split(',')]

    app_config['stats'] = {}
    if config.has_section('stats'):
      for option in config.options('stats'):
        app_config['stats.' + option] = config.get('stats', option)

    app_config['issues'] = {
      'token': config.get('issues', 'token'),
      'repository': config.get('issues', 'repository')
    }

    if config.has_section('static'):
      app_config['static.enabled'] = True
      app_config['static.root'] = config.get('static', 'root')

    # Logging channels
    app_channels = hlib.engine.AppChannels()

    stdout = hlib.log.channels.stdout.Channel()
    stderr = hlib.log.channels.stderr.Channel()

    for channel_type in hlib.engine.AppChannels.CHANNEL_TYPES:
      app_config['log.%s.enabled' % channel_type] = config.getboolean('log.%s' % channel_type, 'enabled')
      if config.has_option('log.%s.format' % channel_type, 'format'):
        app_config['log.%s.format' % channel_type] = config.get('log.%s' % channel_type, 'format')

      channels = []

      for channel_endpoint in config.get('log.%s' % channel_type, 'channels').split(','):
        channel_endpoint = channel_endpoint.strip()

        if channel_endpoint == '<default log>':
          channels.append(hlib.log.channels.file.Channel(os.path.join(config.get('server', 'path'), 'logs', channel_type + '.log')))
        elif channel_endpoint == '<stdout>':
          channels.append(stdout)
        elif channel_endpoint == '<stderr>':
          channels.append(stderr)
        else:
          channels.append(hlib.log.channels.file.Channel(channel_endpoint))

      app_channels.add(channel_type, *channels)

    app = hlib.engine.Application('settlers', root, db, app_config, channels = app_channels, config_file = config)

    # Session storage
    if config.get('session', 'storage') == 'memory':
      app.sessions = hlib.http.session.MemoryStorage(app)
    elif config.get('session', 'storage') == 'cached_memory':
      app.sessions = hlib.http.session.CachedMemoryStorage(config.get('session', 'storage_path'), app)

    hlib.ui.templates.Mako.Template.init_app(app)

    app.config['sessions.time'] = config.getint('session', 'time')
    app.config['sessions.cookie_name']  = config.get('session', 'cookie_name')

    server_config = hlib.server.Server.default_config()
    server_config['server'] = config.get('server', 'host')
    server_config['port']   = config.getint('server', 'port')
    server_config['app']    = app
    server_config['queue.workers'] = config.getint('server', 'queue.workers')
    server_config['queue.timeout'] = config.getint('server', 'queue.timeout')
    server_config['queue.size'] = config.getint('server', 'queue.size')

    self.engine = hlib.engine.Engine('Engine #1', [server_config])

    signal.signal(signal.SIGHUP, self.on_sighup)
    signal.signal(signal.SIGUSR1, self.on_sigusr1)

  def run(self):
    self.engine.start()
