import psycopg2
from pgeo.utils import log
from pgeo.error.custom_exceptions import PGeoException

# Logger
log = log.logger(__name__)

# TODO: use exceptions?


class DBConnection:
    con = None
    datasource = None
    autocommit = True
    schema= None


    def __init__(self, datasource):
        if DBConnection.con is None:
            try:
                log.info("---PostGIS connection initialization---")
                self.datasource = datasource
                if self.datasource["schema"]:
                    self.schema = self.datasource["schema"]
                db_connect_string = self.get_connection_string(False)
                self.con = psycopg2.connect(db_connect_string)
                log.info("Database '%s' connection opened. " % datasource['dbname'] )
            except psycopg2.DatabaseError as db_error:
                log.error("Error :\n{0}".format(db_error))
                raise PGeoException("Error :\n{0}".format(db_error))

    # TODO: autocommit as parameter (FOR BULK)
    def insert(self, table, insert_keys, insert_values, values):
        try:
            self.con.autocommit = self.autocommit
            cur = self.con.cursor()
            # query
            sql = "INSERT INTO " + table + " (" + insert_keys + ") VALUES (" + insert_values + ")"
            cur.execute(sql, values)
            return True
        except Exception, e:
            self.con.rollback()
            log.error("DBConnection.import_data Error: ", e)
            return False

    # TODO: autocommit as parameter (FOR BULK)
    def insert(self, table, values):
        try:
            self.con.autocommit = self.autocommit
            cur = self.con.cursor()
            # query
            sql = "INSERT INTO " + table + " VALUES (" + values + ")"
            cur.execute(sql)
            return True
        except Exception, e:
            self.con.rollback()
            log.error("DBConnection.import_data Error: ", e)
            return False

    def query(self, query):
        try:
            if self.check_query(query):
                cur = self.con.cursor()
                cur.execute(query)
                rows = cur.fetchall()
                return rows
            else:
                return False
        except Exception, e:
            self.con.rollback()
            log.warn("Query error: use raise Exception? " + str(e))

    def __del__(self):
        self.close_connection()

    def __exit__(self):
        self.close_connection()

    def close_connection(self):
        if self.con is not None:
            self.con.close()
            log.info("Database '%s' connection closed. " % self.datasource['dbname'] )

    def get_connection_string(self, add_pg=True):
        db_connection_string = ""
        if add_pg is True:
            db_connection_string += "PG:"
        db_connection_string += "host=%s port='%s' dbname=%s user=%s password=%s" %(self.datasource['host'], self.datasource['port'],self.datasource['dbname'], self.datasource['username'], self.datasource['password'])
        return db_connection_string

    # blacklist methods not allowed
    def check_query(self, query):
        q = query.lower()
        if "insert" in q:
            return False
        if "update" in q:
            return False
        if "delete" in q:
            return False
        return True


# def get_connection_string(database, add_pg=True):
#     db_connection_string = ""
#     if add_pg is True:
#         db_connection_string += "PG:"
#         db_connection_string += "host=%s port='%s' dbname=%s user=%s password=%s" %(database['host'], database['port'],database['dbname'], database['username'], database['password'])
#     return db_connection_string