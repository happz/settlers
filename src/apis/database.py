import sys
from twisted.web import server, resource
from twisted.internet import reactor, endpoints

import ZODB.DB
import ZODB.FileStorage
import relstorage.storage
import relstorage.adapters.mysql
import transaction

from json import dumps, loads
import jwt

import hlib.database
import games
import time
import threading

from . import Logging

import logging

logger = logging.getLogger('ZODB.Connection')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class Database(object):
    def __init__(self, dbpath):
        self._dbpath = dbpath

        self._storage = None
        self._db = None

        self._log = Logging('db')
        self._log.attachTo(self)

    def open(self):
        dbpath = [e.strip() for e in self._dbpath.split(':')]

        if dbpath[0] == 'mysql':
            options = relstorage.options.Options()
            options.keep_history = False
            options.pack_gc = False
            options.cache_local_mb = 100
            options.cache_local_compression = 'none'

            host, port, db, user, password = dbpath[1], dbpath[2], dbpath[3], dbpath[4], dbpath[5]

            adapter = relstorage.adapters.mysql.MySQLAdapter(options = options, host=host, port=int(port), db=db, user=user, passwd=password)
            self._storage = relstorage.storage.RelStorage(adapter, options = options)

        elif dbpath[0] == 'fs':
            self._storage = ZODB.FileStorage.FileStorage(dbpath[1], create = False, read_only = False, pack_gc = False)

        self._db = ZODB.DB(self._storage, pool_size = 2, cache_size = 200000)

    def connect(self):
        conn = self._db.open()
        root = conn.root()['root']

        return conn, root

    def close(self):
        self.DEBUG('close')
        self._db.close()

    def start_transaction(self):
        threading.current_thread().DEBUG('transaction start')

        transaction.abort()
        transaction.begin()

    def commit(self):
        threading.current_thread().DEBUG('db commit')

        try:
            transaction.commit()
            self.doom()

        except ZODB.POSException.ConflictError as e:
            print >> sys.stderr, 'Conflict Error:'
            print >> sys.stderr, '  class_name: ' + str(e.class_name)
            print >> sys.stderr, '  msg: ' + str(e.message)
            print >> sys.stderr, '  data: ' + str(e.args)
            print >> sys.stderr, '  info: ' + str(e.serials)

    def doom(self):
        threading.current_thread().DEBUG('db doom')

        transaction.doom()

    def rollback(self):
        threading.current_thread().DEBUG('db rollback')

        transaction.abort()
        self.doom()

    def cacheStats(self, connection):
        connRepr = repr(connection)

        for details in self._db.cacheDetailSize():
            if connRepr != details['connection']:
                continue

            return {
                'nonGhostCount': details['ngsize']
            }

        return {
            'nonGhostCount': -1
        }
