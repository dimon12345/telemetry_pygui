import psycopg2
import time


class RemoteSqlDatabase:
	connection = None
	def connect(self):
		if self.connection != None:
			return True
		try:
			self.connection = psycopg2.connect(
				host="pg-host",
				database="telemetry",
				user="lexx",
				password="xev")

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
