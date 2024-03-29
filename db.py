import sqlite3
import mysql.connector


class SQLHandler(object):
    def __init__(self,
                 file_name="gcir_news_db",
                 host="192.168.0.10",
                 port="3306",
                 user="gcir_api_admin",
                 password="gcirsaveillusts"):
        self.db = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=file_name
        )
        self.conn = self.db.cursor()

    def get(self, sql, data=None):
        if data == None:
            self.conn.execute(sql)
        else:
            self.conn.execute(sql, data)
        return self.conn.fetchall()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def edit(self, sql, data=None, autoCommit=True):
        try:
            if not data:
                self.conn.execute(sql)
            else:
                self.conn.execute(sql, data)
            if autoCommit:
                self.db.commit()
            return True
        except Exception as e:
            print(e)
            self.db.rollback()
            return False

    def has(self, tableName, condition, data=None):
        d = self.get("SELECT 'T' FROM %s WHERE %s" %
                     (tableName, condition), data)
        if len(d) > 0:
            return True
        else:
            return False

    def close(self):
        self.conn.close()
