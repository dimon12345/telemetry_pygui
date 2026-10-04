
class SensorNames:
	names = {}

	def __init__(self, remoteDb):
		self.remoteDb = remoteDb

	def updateNames(self):
		query = """SELECT name_id, name from names;"""
		cursor = self.remoteDb.getCursor()
		cursor.execute(query)
		records = cursor.fetchall()
		for row in records:
			self.names[row[1]] = row[0]

	def addSensor(self, name):
		query = """CREATE TABLE IF NOT EXISTS names (
			name_id SERIAL PRIMARY KEY,
			name VARCHAR(255) NOT NULL
		)"""
		cursor = self.remoteDb.getCursor()
		cursor.execute(query)
		self.remoteDb.getConnection().commit()

		self.updateNames()

		if name in self.names:
			return self.names[name]

		query = """INSERT INTO names(name)
			VALUES(%s) RETURNING name_id;"""
		cursor = self.remoteDb.getCursor()
		cursor.execute(query, (name,))

		name_id = cursor.fetchone()[0]
		self.remoteDb.getConnection().commit()

		return name_id

	def getSensorId(self, name):
		if not name in self.names:
			return self.addSensor(name)
		return self.names[name]

	def getSensorNames(self):
		if len(self.names) == 0:
			self.updateNames()
		return self.names.keys()
