from datetime import datetime, timedelta, timezone

from Config import PostgresConfig
import RemoteSqlDatabase
import SensorNames


class RemoteSensorsDatabase(RemoteSqlDatabase.RemoteSqlDatabase):
    def __init__(self, pg_config: PostgresConfig):
        super().__init__(pg_config)

        self.setInterval60min()
        self.sensorNames = SensorNames.SensorNames(self)
        self.startTime = datetime.now()

    def resetStartTimer(self):
        self.startTime = datetime.now()
        self.showInterval = False

    def setInterval60min(self):
        self.interval = timedelta(minutes=60)
        self.showInterval = True

    def setInterval6hours(self):
        self.interval = timedelta(hours=6)
        self.showInterval = True

    def setIntervalDay(self):
        self.interval = timedelta(days=1)
        self.showInterval = True

    def setIntervalWeek(self):
        self.interval = timedelta(days=7)
        self.showInterval = True

    def getSensorNames(self):
        return self.sensorNames.getSensorNames()
        self.showInterval = True

    def getData(self, sensorName):
        tData = []
        vData = []

        sensorId = self.sensorNames.getSensorId(sensorName)

        if self.showInterval:
            tableName = "telemetry"
            query = """SELECT value, timestamp from {} WHERE timestamp > %s AND sensor_id = {} ORDER BY timestamp;""".format(tableName, sensorId)
            cursor = self.getCursor()
            try:
                print("query: ", query)
                cursor = self.getCursor()
                cursor.execute(query, (datetime.now(timezone.utc) - self.interval,))
                records = cursor.fetchall()
                print("query done")
                for row in records:
                    vData.append(row[0])
                    tData.append(row[1])
            except Exception as e:
                print("exception: ", e)
            print("request #3")

        return (tData,vData)

