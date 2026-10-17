import psycopg2
import time

from Config import PostgresConfig


class RemoteSqlDatabase:
    def __init__(self, pg_config: PostgresConfig):
        self.pg_config = pg_config
        self.connection = None

    def connect(self):
        if self.connection != None:
            return True
        try:
            print("connect to db",self.pg_config.host, self.pg_config.dbname,
                self.pg_config.user, self.pg_config.password)
            self.connection = psycopg2.connect(
                host=self.pg_config.host,
                database=self.pg_config.dbname,
                user=self.pg_config.user,
                password=self.pg_config.password)
            return True

        except Exception as e: print(e)
        return False

    def getConnection(self):
        while not self.connect():
            print("Can't connect remote database.")
            time.sleep(1)

        return self.connection

    def getCursor(self):
        connection = self.getConnection()
        return connection.cursor()
