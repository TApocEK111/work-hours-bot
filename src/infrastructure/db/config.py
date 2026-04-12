from dataclasses import dataclass

from infrastructure.env import EnvVars, get_env


@dataclass
class DBConfig:
    url: str = ""

    def __post_init__(self):
        if not self.url:
            self.url = f"sqlite+aiosqlite:///{get_env(EnvVars.DB_LOCATION)}"
