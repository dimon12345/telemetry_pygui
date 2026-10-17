#!/usr/bin/env python3

import argparse
import tkinter

from Config import Config, loadConfig
from Settings import Sensor, Settings, SettingsManager
from core.TelemetryService import TelemetryService
from repos.PsycoPg2TelemetryRepository import PsycoPg2TelemetryRepository
from ui.TelemetryPresenter import TelemetryPresenter
from ui.TkinterTelemetryWindow import TkinterTelemetryWindow

def parseArgParams() -> argparse.Namespace:
    parser = argparse.ArgumentParser("PyGUI")
    parser.add_argument(
            "-c", "--config",
            action="store", dest='config_filepath',
            default='config.json',
            help="Config filename (default: config.json)"
    )
    parser.add_argument(
            "-s", "--settings",
            action="store", dest='settings_filepath',
            default='settings.json',
            help="Settings filename (default: settings.json)"
    )
    return parser.parse_args()

class App:
    def __init__(self, config:Config, settings:Settings):
        repository = PsycoPg2TelemetryRepository(config.db)
        service = TelemetryService(repository)
        presenter = TelemetryPresenter(settings, service)
        self.view = TkinterTelemetryWindow(presenter)
        presenter.setView(self.view)

    def mainloop(self) -> None:
        try:
            tkinter.mainloop()
        except KeyboardInterrupt:
            pass

def main() -> None:
    args = parseArgParams()
    config = loadConfig(args.config_filepath)

    with SettingsManager(args.settings_filepath) as settings:
        app = App(config, settings)
        app.mainloop()

if __name__ == "__main__":
    main()
