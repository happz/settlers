class PlayerStats(object):
    def __init__(self, user):
        self.name = user.name

    def toAPI(self):
        raise NotImplementedError()


class GamesStats(object):
    def __init__(self):
        self.records = []
        self.last_refreshed = None

    def get_fresh_stats(self, dbroot):
        raise NotImplementedError()

    def refresh(self, dbroot):
        self.records, self.last_refreshed = self.get_fresh_records(dbroot), time.time()
