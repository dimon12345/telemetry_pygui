from datetime import timedelta

from core.TelemetryRepository import TelemetryRepository
from core.TelemetryService import TelemetryService

from Settings import Settings, Sensor
from ui.TelemetryView import TelemetryView

class TelemetryPresenter:
    def __init__(self,
            settings:Settings,
            service:TelemetryService,
    ):
        self.view: TelemetryView | None = None
        self.settings = settings
        self.service = service
        self.interval = timedelta(hours=1)

    def setView(self, view:TelemetryView) -> None:
        self.view = view
        self.view.setupView()
        self.view.setTitle("Telemetry")
        self.loadSettings()
        self.updateSettingsPanel()
        self.updatePlot()

    def loadSettings(self) -> None:
        self.view.setFullscreen(self.settings.fullscreen)

        sensors = self.service.getSensors()
        if self.settings.sensors:
            for name in sensors:
                if name not in self.settings.sensors:
                    self.settings.sensors[name] = Sensor(enabled=True)
                    self.service.enableSensor(name, True)
                else:
                    enabled = self.settings.sensors[name].enabled
                    self.service.enableSensor(name, enabled)
        else:
            for name in sensors:
                self.settings.sensors[name] = Sensor(enabled=True)
                self.service.enableSensor(name, True)

    def updateSettingsPanel(self) -> None:
        if self.settings.hide_settings:
            self.view.hideSettingsPanel()
        else:
            enabled_sensors = self.service.getEnabledSensors()
            self.view.showSettingsPanel(enabled_sensors)

    def updatePlot(self) -> None:
        plot_data = self.service.getPlotData(self.interval)
        self.view.setPlotData(plot_data)

    def onF11Key(self) -> None:
        fullscreen = not self.settings.fullscreen
        self.settings.fullscreen = fullscreen
        self.view.setFullscreen(fullscreen)

    def onEscapeKey(self) -> None:
        if self.settings.fullscreen:
            self.settings.fullscreen = False
            self.view.setFullscreen(False)
        else:
            self.view.destroyView()

    def onSettingsButton(self) -> None:
        self.settings.hide_settings = not self.settings.hide_settings
        self.updateSettingsPanel()

    def onFullscreenButton(self) -> None:
        self.settings.fullscreen = not self.settings.fullscreen
        self.view.setFullscreen(self.settings.fullscreen)

    def setInterval(self, interval:timedelta) -> None:
        self.interval = interval
        plot_data = self.service.getPlotData(self.interval)
        self.view.setPlotData(plot_data)

    def onAnimate(self) -> None:
        self.updatePlot()

    def onSensorCheckbutton(self, name:str) -> None:
        enabled_sensors = self.service.getEnabledSensors()
        checked = enabled_sensors[name]
        self.settings.sensors[name].enabled = not checked
        self.service.enableSensor(name, not checked)
        self.updatePlot()
