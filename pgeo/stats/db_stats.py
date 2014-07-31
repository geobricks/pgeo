from pgeo.db.postgresql.common import DBConnection


class DBStats:

    db = None
    schema=None
    datasource=None

    def __init__(self, datasource):
        if self.db is None:
            self.datasource = datasource
            self.db = DBConnection(self.datasource)
            self.schema = self.db.schema

    def insert_stats(self, table, data):
        try:
            return self.db.insert(table, data)
        except Exception, e:
            return False

    def query(self, query):
        return self.db.query(query)

    def get_connection_string(self, add_pg=True):
        db_connection_string = ""
        if add_pg is True:
            db_connection_string += "PG:"
            db_connection_string += "host=%s port='%s' dbname=%s user=%s password=%s" %(self.datasource['host'], self.datasource['port'],self.datasource['dbname'], self.datasource['username'], self.datasource['password'])
        return db_connection_string
