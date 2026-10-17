from datetime import datetime, timedelta, timezone

from core.SensorPlotData import SensorPlotData

class TelemetryService:
    def __init__(self, repository:TelemetryRepository):
        self.repository = repository
        self.sensors = self.repository.getSensors()
        self.enabled = {}
        for name in self.sensors:
            self.enabled[name] = False

    def getPlotData(self, interval:timedelta):
        plot_data = {}
        for sensor_name in self.enabled:
            if not self.enabled[sensor_name]:
                continue
            sensor_id = self.sensors[sensor_name]
            time_data = []
            value_data = []
            for telemetry in self.repository.getTelemetryIterator(
                sensor_id,
                datetime.now(timezone.utc) - interval
            ):
                value_data.append(telemetry[0])
                time_data.append(telemetry[1])

            plot_data[sensor_name] = SensorPlotData(time_data, value_data)

        return plot_data

    def getSensors(self):
        return self.sensors.keys()

    def enableSensor(self, name:str, enable:bool=True):
        self.enabled[name] = enable

    def getEnabledSensors(self):
        return self.enabled
