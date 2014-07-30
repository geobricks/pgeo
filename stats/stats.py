from config import settings
from db_stats import DBStats


class Stats():

    config = settings.stats
    db = None

    def __init__(self, config=None):
        # merge settings with
        self.get_default_db()

        return None

    def get_default_db(self):
        for item in settings.db["stats_db"]["dbs"]:
            if item["id"] in self.config["db"]["stats_default_db"]:
                self.db = DBStats(item)
                return None
        return None

stats = Stats()