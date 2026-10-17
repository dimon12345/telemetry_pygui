import json
import os
from pydantic import BaseModel


class PostgresConfig(BaseModel):
    host: str
    user: str
    password: str
    dbname: str

class Config(BaseModel):
    db: PostgresConfig

config_instance = Config(
    db=PostgresConfig(
            host="pg-host",
            user="telemetry",
            password="telemetry",
            dbname="telemetry"
    )
)

def loadConfig(filepath: str) -> Config:
    if os.path.isfile(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Config.model_validate(data)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(config_instance.model_dump_json(indent=4))
        return config_instance
