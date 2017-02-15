from . import APIHandler, API_SUCCESS, API_FAIL, api

class AdminHandler(APIHandler):
    @api('/admin/maintenance/', readOnly = False, requiresAdmin = True, schema = {
        'enabled': {
            'type': 'boolean',
            'required': False
        }
    })
    def handle_admin_maintenance(self, request, dbroot, user = None, enabled = None):
        if enabled is not None:
            dbroot.server.maintenance_mode = enabled

        return API_SUCCESS({
            'enabled': dbroot.server.maintenance_mode
        })


    @api('/admin/maintenance/access/', requiresAdmin = True)
    def handle_admin_maintenance_access(self, request, dbroot, user = None):
        return API_SUCCESS({
            'users': [ user.toAPI() for user in dbroot.users.values() if user.maintenance_access is True ]
        })


    @api('/admin/maintenance/access/grant', readOnly = False, requiresAdmin = True, schema = {
        'username': 'username'
    })
    def handle_admin_maintenance_access_grant(self, request, dbroot, user = None, username = None):
        if username not in dbroot.users:
            return API_FAIL('Invalid username')

        user = dbroot.users[username]

        user.maintenance_access = True
        request.bus.publish('user.modified', user)

        return API_SUCCESS()


    @api('/admin/maintenance/access/revoke', readOnly = False, requiresAdmin = True, schema = {
        'username': 'username'
    })
    def handle_admin_maintenance_access_revoke(self, request, dbroot, user = None, username = None):
        if username not in dbroot.users:
            return API_FAIL('Invalid username')

        user = dbroot.users[username]

        user.maintenance_access = False
        request.bus.publish('user.modified', user)

        return API_SUCCESS()
