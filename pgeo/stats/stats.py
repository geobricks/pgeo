from pgeo.stats.db_stats import DBStats
from pgeo.utils import log


class Stats():

    # default settings
    settings = None
    db = None

    def __init__(self, settings=None):

        self.settings = settings
        self.db = self.get_default_db()


    def zonalstats(self):
        return None

    # get the default db from the settings
    def get_default_db(self):
        try:
            if self.settings["stats"]:
                if self.settings["db"]:
                    db = self.settings["stats"]["db"]["stats"]
                    return DBStats(self.settings["db"][db])
        except:
            log.logger(__name__).warn("No db found")
            pass



