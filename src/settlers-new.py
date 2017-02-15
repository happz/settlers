import argparse
import sys
from twisted.web import server, resource
from twisted.internet import reactor, endpoints

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', dest='db', default=None, action='store', required=True)

    group = parser.add_argument_group('HTTP listening')
    group.add_argument('--host', dest='host', default='', action='store')
    group.add_argument('--port', dest='port', default=9080, action='store', type=int)
    group.add_argument('--queue', dest='queue', default=50, action='store', type=int)

    args = parser.parse_args()

    from apis import log

    log.debug('Opening database: db="%s"' % args.db)

    from apis.database import Database
    db = Database(args.db)
    db.open()

    from apis import Handler
    from apis.admin import AdminHandler
    from apis.board import BoardHandler
    from apis.home import HomeHandler
    from apis.root import RootHandler
    from apis.settings import SettingsHandler

    _ = BoardHandler()
    _ = HomeHandler()
    _ = RootHandler()
    _ = SettingsHandler()
    _ = AdminHandler()

    handler = Handler(db)

    log.debug('Binding to a port: port=%s' % args.port)

    site = server.Site(handler)
    endpoint = endpoints.TCP4ServerEndpoint(reactor, args.port, interface=args.host, backlog=args.queue)
    endpoint.listen(site)

    reactor.getThreadPool().adjustPoolsize(minthreads=0, maxthreads=30)

    log.info('Starting a reactor loop...')
    log.debug('Serves following URIs:')
    for uri in handler.availableURIs():
        log.debug('  ' + uri)

    reactor.run()

    db.close()
