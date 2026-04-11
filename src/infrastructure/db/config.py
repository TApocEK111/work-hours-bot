from dataclasses import dataclass

@dataclass
class DBConfig:
    url: str = "sqlite+aiosqlite:///./data/work_hours.sqlite3"