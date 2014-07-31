from config import settings
from pgeo.pgeo.stats.db_stats import DBStats


class Stats():

    # default settings
    config = None
    db = None

    def __init__(self, config=None):

        self.config = config
        # merge settings with
        self.get_default_db()
        return None

    def zonalstats(self):
        return None

    # get the default db from the settings
    def get_default_db(self):
        if settings.db:
            for item in settings.db["stats_db"]["dbs"]:
                if item["id"] in self.config["db"]["stats_default_db"]:
                    self.db = DBStats(item)
                    return None
        return None