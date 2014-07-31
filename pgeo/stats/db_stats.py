from pgeo.db.postgresql.common import DBConnection

class DBStats:

    db = None

    def __init__(self, datasource):
        if self.db is None:
            self.db = DBConnection(datasource)

    def insert_stats(self, table, data ):
        try:
            return self.db.insert(table, data)
        except Exception, e:
            return False

    def query(self, query ):
        return self.db.query(query)
