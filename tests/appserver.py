import ConfigParser
import os
import os.path
import shutil
import signal
import subprocess
import sys
import time

from hlib.tests import *

class AppServer(object):
  _appservers = {}

  @staticmethod
  def fetch_config(section):
    from testconfig import config

    dir = config[section]['dir'].strip()
    if not os.path.isabs(dir):
      dir = os.path.join(config['paths']['tmpdir'].strip(), dir)

    interpret = config[section]['interpret'].strip()

    starter = config[section]['starter'].strip()
    if not os.path.isabs(starter):
      starter = os.path.join(config['paths']['rootdir'].strip(), starter)

    config_file = config[section]['config_file'].strip()
    if not os.path.isabs(config_file):
      config_file = os.path.join(config['paths']['rootdir'].strip(), config_file)

    url = config[section]['url'].strip() if 'url' in config[section] else None

    return (dir, interpret, starter, config_file, url)

  def __init__(self, dir, interpret, starter, config_file, url):
    super(AppServer, self).__init__()

    self.init_done = False
    self.running = False
    self.pid = None

    self.dir = dir

    self.interpret = interpret
    self.starter = starter
    self.config_file = config_file
    self.real_config_file = os.path.join(self.dir, 'appserver.conf')
    self.url = url

    self.dbdir = os.path.join(dir, 'database')

    self.stdout = os.path.join(dir, 'stdout.log')

    self.config = ConfigParser.ConfigParser()
    self.config.read(self.config_file)

    self.config.set('database', 'address', 'FileStorage:::::%s/db' % self.dbdir)
    self.config.set('log', 'access', os.path.join(dir, 'access.log'))
    self.config.set('log', 'error', os.path.join(dir, 'error.log'))
    self.config.set('log', 'transactions', os.path.join(dir, 'transactions.log'))
    self.config.set('log', 'events', os.path.join(dir, 'events.log'))
    self.config.set('session', 'storage_path', os.path.join(dir, 'sessions.dat'))

  def dbinit(self, root):
    from testconfig import config

    import lib
    import lib.datalayer

    root['root'] = lib.datalayer.Root()
    root = root['root']

    # Test user
    root.users[config['web']['username']] = lib.datalayer.User(config['web']['username'], lib.pwcrypt(config['web']['password']), config['web']['email'])

    # Additional users
    for i in range(0, 20):
      username = 'Dummy User #%i' % i
      root.users[username] = lib.datalayer.User(username, lib.pwcrypt(''), 'a@b.cz')

    # Trumpet
    import lib.trumpet
    trumpet = {'subject': '', 'text': ''}
    __setter = lambda cls: getattr(root.trumpet, cls.__name__).update(trumpet)
    __setter(lib.trumpet.PasswordRecoveryMail)
    __setter(lib.trumpet.Board)
    __setter(lib.trumpet.VacationTermination)

  def execute_in_db(self, fn, *args, **kwargs):
    start_after = self.running

    if self.running:
      self.stop()

    import hlib.database

    address = hlib.database.DBAddress(self.config.get('database', 'address'))
    db = hlib.database.DB(self.dir + '-db', address)

    db.open()
    conn, root = db.connect()

    fn(root, *args, **kwargs)

    db.commit()

    conn.close()
    db.close()

    if start_after:
      self.start()

  def init(self):
    if os.path.exists(self.dir):
      shutil.rmtree(self.dir)

    if not os.path.exists(self.dir):
      os.makedirs(self.dir)

    if not os.path.exists(self.dbdir):
      os.makedirs(self.dbdir)

    with open(self.real_config_file, 'w') as f:
      self.config.write(f)

    self.execute_in_db(self.dbinit)

    # And we're done with setup
    self.init_done = True

  def start(self):
    if not self.init_done:
      self.init()

    cmd = [self.interpret, self.starter, '-c', self.real_config_file]

    stdout = open(self.stdout, 'w')

    self.pid = subprocess.Popen(cmd, stdout = stdout).pid
    self.running = True

    time.sleep(10)

  def stop(self):
    if self.pid:
      os.kill(self.pid, signal.SIGKILL)
      self.pid = None

    self.running = False

  def destroy(self):
    if self.pid:
      self.stop()

    shutil.rmtree(self.dir)
