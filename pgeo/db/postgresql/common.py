import psycopg2

# TODO: use exceptions?


class DBConnection:
    con = None
    datasource = None
    autocommit = True

    def __init__(self, datasource):
        if DBConnection.con is None:
            try:
                self.datasource = datasource
                db_connect_string = self.get_connection_string(False)
                self.con = psycopg2.connect(db_connect_string)
                print('Database %s connection opened. ' % self.datasource['dbname'] )
            except psycopg2.DatabaseError as db_error:
                print("Error :\n{0}".format(db_error))

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
            print "DBConnection.import_data Error: ", e
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
            print "DBConnection.import_data Error: ", e
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
            print "use raise Exception?"

    def __del__(self):
        self.close_connection()

    def __exit__(self):
        self.close_connection()

    def close_connection(self):
        if self.con is not None:
            self.con.close()
            print('Database %s connection closed. ' % self.datasource['dbname'] )

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