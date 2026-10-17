from datetime import datetime
import psycopg2
from typing import Iterator

from core.TelemetryRepository import TelemetryRepository
from Config import PostgresConfig

class PsycoPg2TelemetryRepository(TelemetryRepository):
    def __init__(self, config: PostgresConfig):
        self.connection = psycopg2.connect(
                host=config.host,
                database=config.dbname,
                user=config.user,
                password=config.password
        )

    def getSensors(self) -> dict[str, int]:
        query = """SELECT * from sensors;"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()

        sensors = {}
        for row in records:
            sensors[row[1]] = row[0]
        return sensors

    def getTelemetryIterator(self, sensor_id:int, begin_time:datetime, batch_size:int = 1000) -> Iterator[tuple]:
        query = ("""SELECT value, timestamp from telemetry WHERE timestamp > %s """
                """AND sensor_id = {} ORDER BY timestamp;""".format(sensor_id))
        cursor = self.connection.cursor()
        cursor.execute(query, (begin_time,))

        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
              break

            for row in rows:
              yield row
