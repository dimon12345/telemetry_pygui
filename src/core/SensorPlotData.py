from dataclasses import dataclass

@dataclass
class SensorPlotData:
    time_data: list[str]
    value_data: list[float]
