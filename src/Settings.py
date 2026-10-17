import json
import os
from pydantic import BaseModel
from typing import Dict


class Sensor(BaseModel):
    disabled: bool = False

class Settings(BaseModel):
    hide_settings: bool = False
    fullscreen: bool = False
    sensors: Dict[str, Sensor]

raw_settings = {
    "hide_settings": False,
    "fullscreen": False,
    "sensors": {}
}

settings_instance = Settings.model_validate(raw_settings)

class SettingsManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.settings = {}

    def __enter__(self):
        if os.path.exists(self.filepath):
            self.settingsLoad()
        else:
            self.settings = settings_instance
            self.saveSettings()
        return self.settings

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.saveSettings()
        return False

    def saveSettings(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.write(self.settings.model_dump_json(indent=4))
        except IOError as e:
            print(f"Save settings error: {e}")

    def settingsLoad(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.settings = Settings.model_validate(data)
