from datetime import datetime
from typing import Iterator, Protocol

class TelemetryRepository(Protocol):
    def getSensors(self) -> dict[str, int]: ...
    def getTelemetryIterator(self, sensor_id:int, begin_time:datetime,
            batch_size:int = 100) -> Iterator[tuple]: ...
