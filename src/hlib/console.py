__author__ = 'Milos Prchlik'
__copyright__ = 'Copyright 2010 - 2013, Milos Prchlik'
__contact__ = 'happz@happz.cz'
__license__ = 'http://www.php-suit.com/dpl'

import argparse
import json
import os

import hlib.locks

class HelpAction(argparse._HelpAction):
  def __init__(self, *args, **kwargs):
    super(HelpAction, self).__init__(*args, **kwargs)

  def __call__(self, parser, namespace, values, option_string=None):
    parser.print_help()

class CommandException(Exception):
  def __init__(self, message, *args, **kwargs):
    super(CommandException, self).__init__(*args, **kwargs)

    self.data = {'status': 'ERROR', 'message': message}

class CommandParser(argparse.ArgumentParser):
  def error(self, message):
    raise CommandException(message)

class Command(object):
  def __init__(self, console, parser):
    super(Command, self).__init__()

    self.console = console
    self.parser = parser

  def handler(self, *args, **kwargs):
    return {}

class Command_Sys(Command):
  def __init__(self, console, parser):
    super(Command_Sys, self).__init__(console, parser)

    self.parser.add_argument('--quit', action = 'store_const', dest = 'action', const = 'quit')
    self.parser.add_argument('--version', action = 'store_const', dest = 'action', const = 'version')
    self.parser.add_argument('--crash', action = 'store_const', dest = 'action', const = 'crash')

    self.parser.add_argument('--locks', action = 'store_const', dest = 'action', const = 'locks')

  def handler(self, args):
    if args.action == 'quit':
      self.console.stop()
      self.console.engine.stop()
      return

    if args.action == 'crash':
      os._exit(0)

    if args.action == 'locks':
      hlib.locks.save_stats('lock_debug.dat')

class Command_Help(Command):
  def __init__(self, console, parser):
    super(Command_Help, self).__init__(console, parser)

  def handler(self, args):
    return {'commands': self.console.commands.keys()}

class Console(object):
  def __init__(self, name, engine, stdin, stdout):
    super(Console, self).__init__()

    self.name = name
    self.engine = engine
    self.stdin = stdin
    self.stdout = stdout

    self.keep_running = True

    self.parser = CommandParser()
    self.parser.register('action', 'help', HelpAction)
    self.subparsers = self.parser.add_subparsers(dest = 'subparser_name')

    self.commands = {}

    self.register_command('sys', Command_Sys)
    self.register_command('?', Command_Help)

  def register_command(self, name, cls, *args, **kwargs):
    subparser = self.subparsers.add_parser(name)
    subparser.register('action', 'help', HelpAction)
    self.commands[name] = cls(self, subparser, *args, **kwargs)

  def err_required_arg(self, name):
    raise CommandException('Option \'%s\' is required' % name)

  def stop(self):
    self.keep_running = False

  def __read(self, prompt):
    self.stdout.write(prompt)
    self.stdout.flush()

    line = self.stdin.readline()
    if not len(line):
      return None

    return line.strip()

  def cmdloop(self):
    while self.keep_running:
      s = self.__read('console# ')
      if s == None:
        continue

      output = {'status': 'ERROR', 'message': 'No output produced'}

      s = s.strip()
      if len(s) <= 0:
        continue

      try:
        args = self.parser.parse_args(s.split(' '))
        cmd = self.commands.get(args.subparser_name, None)

        if not cmd:
          raise CommandException('Unknown command')

        output = cmd.handler(args)

        if output == None:
          output = {'status': 'OK'}

        if 'status' not in output:
          output['status'] = 'OK'

      except CommandException, e:
        output = e.data

      json.dump(output, self.stdout, sort_keys = True, indent = 4, separators = (',', ': '))
      self.stdout.write('\n')
