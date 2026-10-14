
class SensorNames:
    names = {}

    def __init__(self, remoteDb):
        self.remoteDb = remoteDb

    def loadNames(self):
        query = """SELECT id, name from sensors;"""
        cursor = self.remoteDb.getCursor()
        cursor.execute(query)
        records = cursor.fetchall()
        for row in records:
            self.names[row[1]] = row[0]

    def addSensor(self, name):
        self.loadNames()

        if name in self.names:
            return self.names[name]

        query = """INSERT INTO sensors(name)
            VALUES(%s) RETURNING id;"""
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
            self.loadNames()
        return self.names.keys()
